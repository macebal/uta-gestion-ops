"""
Script to load test data from CSV files into the database.

This script reads CSV files from tests/data/ and populates the database
with accounts, providers, details, payment orders, and invoices.

Usage:
    python scripts/load_test_data.py
    or
    make create-test-data
"""

import csv
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Account, AccountSequence, Supplier, Detail, PaymentOrder, Invoice


DATABASE_URL = "sqlite:///gestion_ops.db"
DATA_DIR = Path("tests/data")


def load_csv(filename):
    """Load CSV file and return list of dictionaries"""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def check_database_status(session):
    """Check if database already contains data and prompt user"""
    existing_orders = session.query(PaymentOrder).count()
    existing_accounts = session.query(Account).count()
    existing_providers = session.query(Supplier).count()
    
    if existing_orders > 0 or existing_accounts > 0 or existing_providers > 0:
        print("\nWARNING: Database already contains data!")
        print(f"   - Accounts: {existing_accounts}")
        print(f"   - Providers: {existing_providers}")
        print(f"   - Payment Orders: {existing_orders}")
        print("\nThis command is designed to populate a fresh database.")
        print("Loading test data into an existing database may cause:")
        print("  - Duplicate entries")
        print("  - Sequence number conflicts")
        print("  - Data inconsistencies")
        
        response = input("\nDo you want to continue anyway? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\nAborted by user.")
            sys.exit(0)
        print()


def load_test_data():
    """Load all test data from CSV files into the database"""
    print("=" * 60)
    print("Loading Test Data from CSV files")
    print("=" * 60)
    
    db_path = Path("gestion_ops.db")
    db_exists = db_path.exists()
    
    if not db_exists:
        print("\nDatabase does not exist. Creating new database...")
    else:
        print(f"\nUsing existing database: {db_path}")
    
    engine = create_engine(DATABASE_URL, echo=False)
    
    print("Ensuring all tables exist...")
    Base.metadata.create_all(engine)
    
    if not db_exists:
        print("Database and tables created successfully!")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        check_database_status(session)
        
        print("\nLoading accounts...")
        accounts_data = load_csv("accounts.csv")
        accounts_map = {}
        
        for row in accounts_data:
            account = Account(
                name=row['name'],
                number=row['number']
            )
            session.add(account)
            session.flush()
            accounts_map[row['number']] = account
            print(f"  Created account: {account.name} ({account.number})")
        
        print("\nCreating account sequences...")
        for account_number, account in accounts_map.items():
            if "Sindical" in account.name:
                last_order = 1000
                last_check = 5000
            elif "Obra Social" in account.name:
                last_order = 1000
                last_check = 5000
            elif "Promocion" in account.name:
                last_order = 1000
                last_check = 5000
            else:
                last_order = 0
                last_check = 0
            
            seq = AccountSequence(
                account_id=account.id,
                last_order_number=last_order,
                last_check_number=last_check
            )
            session.add(seq)
            print(f"  Created sequence for {account.name}: order={last_order}, check={last_check}")
        
        session.flush()
        
        print("\nLoading providers...")
        providers_data = load_csv("providers.csv")
        providers_map = {}
        
        for row in providers_data:
            supplier = Supplier(
                name=row['name'],
                cuit=row['cuit'],
                phone=row['phone'],
                email=row['email']
            )
            session.add(supplier)
            session.flush()
            providers_map[row['name']] = supplier
            print(f"  Created provider: {supplier.name} ({supplier.cuit})")
        
        print("\nLoading payment details...")
        details_data = load_csv("details.csv")
        details_map = {}
        
        for row in details_data:
            detail = Detail(value=row['value'])
            session.add(detail)
            session.flush()
            details_map[row['value']] = detail
            print(f"  Created detail: {detail.value}")
        
        print("\nLoading payment orders...")
        payment_orders_data = load_csv("payment_orders.csv")
        payment_orders_map = {}
        
        for row in payment_orders_data:
            account = accounts_map.get(row['account_number'])
            supplier = providers_map.get(row['supplier_name'])
            detail = details_map.get(row['detail_value'])
            
            if not account:
                print(f"  Warning: Account {row['account_number']} not found, skipping order {row['order_number']}")
                continue
            if not supplier:
                print(f"  Warning: Supplier {row['supplier_name']} not found, skipping order {row['order_number']}")
                continue
            if not detail:
                print(f"  Warning: Detail '{row['detail_value']}' not found, skipping order {row['order_number']}")
                continue
            
            order_date = datetime.strptime(row['order_date'], '%Y-%m-%d').date()
            issue_date = datetime.strptime(row['issue_date'], '%Y-%m-%d').date()
            due_date = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
            
            payment_order = PaymentOrder(
                order_number=int(row['order_number']),
                check_number=int(row['check_number']),
                account_id=account.id,
                supplier_id=supplier.id,
                detail_id=detail.id,
                withholding_amount=Decimal(row['withholding_amount']),
                amount=Decimal(row['amount']),
                order_date=order_date,
                issue_date=issue_date,
                due_date=due_date
            )
            session.add(payment_order)
            session.flush()
            payment_orders_map[int(row['order_number'])] = payment_order
            
            if int(row['order_number']) % 10 == 0:
                print(f"  Created {len(payment_orders_map)} payment orders...")
        
        print(f"  Created total {len(payment_orders_map)} payment orders")
        
        print("\nLoading invoices...")
        invoices_data = load_csv("invoices.csv")
        invoice_count = 0
        
        for row in invoices_data:
            payment_order = payment_orders_map.get(int(row['payment_order_number']))
            supplier = providers_map.get(row['supplier_name'])
            
            if not payment_order:
                print(f"  Warning: Payment order {row['payment_order_number']} not found, skipping invoice {row['invoice_number']}")
                continue
            if not supplier:
                print(f"  Warning: Supplier '{row['supplier_name']}' not found, skipping invoice {row['invoice_number']}")
                continue
            
            invoice = Invoice(
                payment_order_id=payment_order.id,
                invoice_number=row['invoice_number'],
                amount=Decimal(row['amount']),
                supplier_id=supplier.id
            )
            session.add(invoice)
            invoice_count += 1
            
            if invoice_count % 20 == 0:
                print(f"  Created {invoice_count} invoices...")
        
        print(f"  Created total {invoice_count} invoices")
        
        session.commit()
        
        print("\n" + "=" * 60)
        print("SUCCESS! Test data loaded successfully")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  Accounts:        {len(accounts_map)}")
        print(f"  Sequences:       {len(accounts_map)}")
        print(f"  Providers:       {len(providers_map)}")
        print(f"  Details:         {len(details_map)}")
        print(f"  Payment Orders:  {len(payment_orders_map)}")
        print(f"  Invoices:        {invoice_count}")
        print(f"\nDatabase: {DATABASE_URL}")
        print("\nYou can now run the application with: make run")
        print("Or generate a check list with: python generate_check_list.py")
        print()
        
    except FileNotFoundError as e:
        session.rollback()
        print(f"\nERROR: {e}")
        print("\nMake sure you're running this from the project root directory")
        print("and that all CSV files exist in tests/data/")
        sys.exit(1)
    
    except Exception as e:
        session.rollback()
        print(f"\nERROR loading test data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        session.close()


if __name__ == '__main__':
    load_test_data()

