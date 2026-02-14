from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from api_expenses.models import Expense
from api_budgets.models import BudgetCategory, Budget

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with 10 budget categories and 30 days of expenses distributed across them"

    def handle(self, *args, **kwargs):
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("No users found"))
            return

        # Define 10 budget categories with their allocation percentages
        budget_config = {
            'Food & Groceries': Decimal('25'),
            'Transportation': Decimal('15'),
            'Utilities': Decimal('12'),
            'Entertainment': Decimal('10'),
            'Shopping': Decimal('12'),
            'Health & Fitness': Decimal('8'),
            'Dining & Restaurants': Decimal('10'),
            'Insurance': Decimal('5'),
            'Subscriptions': Decimal('2'),
            'Miscellaneous': Decimal('1'),
        }

        # Create budget categories and allocate amounts
        category_objs = []
        total_budget = Decimal('15000')  # Total budget per month
        
        today = timezone.now().date()
        
        self.stdout.write(self.style.WARNING("📋 Creating 10 budget categories..."))
        
        for category_name, percentage in budget_config.items():
            cat, created = BudgetCategory.objects.get_or_create(
                user=user,
                name=category_name
            )
            category_objs.append(cat)
            
            status = "✅ Created" if created else "♻️ Exists"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{status} - {category_name} ({percentage}%)"
                )
            )

        # Create budgets for last 6 months AND next 3 months (to support various date ranges)
        self.stdout.write(self.style.WARNING("\n💰 Creating monthly budgets for last 6 months + next 3 months..."))
        
        for month_offset in range(-6, 4):  # 6 months back, 3 months forward + current
            # Calculate month to create budget for
            budget_month = (today + relativedelta(months=month_offset)).replace(day=1)
            
            self.stdout.write(self.style.WARNING(f"\n  📅 Month: {budget_month.strftime('%B %Y')}"))
            
            for category_name, percentage in budget_config.items():
                cat = BudgetCategory.objects.get(user=user, name=category_name)
                
                # Calculate allocated amount for this category
                allocated_amount = (total_budget * percentage / Decimal('100')).quantize(Decimal('0.01'))
                
                # Create or update budget for this month
                budget, budget_created = Budget.objects.get_or_create(
                    user=user,
                    category=cat,
                    month=budget_month,
                    defaults={'amount': allocated_amount}
                )
                
                if not budget_created:
                    budget.amount = allocated_amount
                    budget.save()
                
                if budget_created:
                    self.stdout.write(
                        f"    ✅ {category_name}: ${allocated_amount}"
                    )

        # Distribute 30 days of expenses across categories based on allocations
        self.stdout.write(self.style.WARNING("\n📊 Seeding 30 days of expenses..."))

        expense_counter = 0

        for i in range(30):
            expense_date = today - timedelta(days=i)
            
            # Distribute expenses evenly across categories
            category_idx = expense_counter % len(category_objs)
            category = category_objs[category_idx]
            
            # Generate realistic random amount (within range based on category)
            amount = Decimal(random.randint(50, 300))
            
            Expense.objects.create(
                user=user,
                category=category,
                amount=amount,
                notes=f"Auto expense - {category.name}",
                date=expense_date
            )
            
            expense_counter += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Seeding completed successfully!\n"
                f"   • Budget Categories: 10\n"
                f"   • Total Monthly Budget: ${total_budget}\n"
                f"   • Budgets Created For: Last 6 months + Next 3 months (9 total)\n"
                f"   • Expenses Created: 30 (last 30 days)\n"
                f"   • Time Period: Last 30 days\n"
                f"   • Coverage: Full year historical + forward planning"
            )
        )
