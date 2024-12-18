import os
import sys
import django
import random

from faker import Faker

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank.settings')
django.setup()

from api.models import Branch, Bankomat

fake = Faker()

def create_random_data():
    num_branches = 5
    min_bankomats_per_branch = 1
    max_bankomats_per_branch = 4

    for _ in range(num_branches):
        branch_address = fake.address()
        open_time = fake.time(pattern='%H:%M:%S', end_datetime=None)
        close_time = fake.time(pattern='%H:%M:%S', end_datetime=None)

        if open_time > close_time:
            open_time, close_time = close_time, open_time
        
        branch = Branch.objects.create(
            address=branch_address,
            open_time=open_time,
            close_time=close_time
        )
        print(f"Branch created: {branch_address}, Open: {open_time}, Close: {close_time}")

        num_bankomats = random.randint(min_bankomats_per_branch, max_bankomats_per_branch)
        for _ in range(num_bankomats):
            cash_deposit = random.choice([True, False])
            Bankomat.objects.create(
                address=branch,
                cash_deposit=cash_deposit
            )
            print(f"  Bankomat created: Branch: {branch_address}, Cash Deposit: {cash_deposit}")
            
            
if __name__ == "__main__":
    create_random_data()