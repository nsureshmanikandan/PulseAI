"""
Generate 4 realistic Excel datasets for PulseAI use-case demos.
  1. Banking_LoanPortfolio.xlsx   - Loan risk management
  2. Insurance_Claims.xlsx        - Claims analytics & fraud detection
  3. Retail_Sales.xlsx            - Sales performance & product intelligence
  4. HR_Workforce.xlsx            - People analytics & attrition
"""
import random
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

random.seed(42)
OUT = Path(r"C:\Users\n.sureshmanikandan\Repo1\PulseAI\test_data")
OUT.mkdir(parents=True, exist_ok=True)

# ── helpers ──────────────────────────────────────────────────────────────────
def rand_date(start="2022-01-01", end="2024-12-31"):
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    return s + timedelta(days=random.randint(0, (e - s).days))

def style_wb(path):
    """Apply header styling to every sheet in the workbook."""
    wb = load_workbook(path)
    hdr_fill   = PatternFill("solid", fgColor="0F172A")
    hdr_font   = Font(bold=True, color="60A5FA", size=10)
    alt_fill   = PatternFill("solid", fgColor="1E293B")
    norm_fill  = PatternFill("solid", fgColor="0F172A")
    thin = Side(style="thin", color="334155")
    border = Border(bottom=Side(style="thin", color="1E3A5F"))

    for ws in wb.worksheets:
        for col_idx, col in enumerate(ws.iter_cols(min_row=1, max_row=1), 1):
            for cell in col:
                cell.fill = hdr_fill
                cell.font = hdr_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = border
        for row in ws.iter_rows(min_row=2):
            row_idx = row[0].row
            fill = alt_fill if row_idx % 2 == 0 else norm_fill
            for cell in row:
                cell.fill = fill
                cell.font = Font(color="CBD5E1", size=9)
                cell.alignment = Alignment(vertical="center")
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 4, 30)
        ws.freeze_panes = "A2"
    wb.save(path)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Banking_LoanPortfolio.xlsx
# ══════════════════════════════════════════════════════════════════════════════
print("Generating Banking_LoanPortfolio.xlsx ...")

LOAN_TYPES    = ["Personal", "Mortgage", "Auto", "Business", "Education", "Revolving Credit"]
LOAN_STATUS   = (["Active"]*55 + ["Closed"]*20 + ["Default"]*12 + ["Watch"]*8 + ["Restructured"]*5)
CITIES        = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad"]
SEGMENTS      = ["Retail", "SME", "Corporate", "Wealth", "Priority"]
COLLATERAL    = ["Property", "Vehicle", "FD", "Shares", "None"]

n = 300
loan_ids      = [f"L{i:05d}" for i in range(1, n+1)]
cust_ids      = [f"C{random.randint(1,200):05d}" for _ in range(n)]
loan_types    = [random.choice(LOAN_TYPES) for _ in range(n)]
principal     = [round(random.uniform(10000, 750000), 2) for _ in range(n)]
interest_rate = [round(random.uniform(6.5, 18.5), 2) for _ in range(n)]
tenure_months = [random.choice([12, 24, 36, 48, 60, 84, 120, 180, 240]) for _ in range(n)]
outstanding   = [round(p * random.uniform(0.1, 0.95), 2) for p in principal]
emi           = [round(o / (t * 0.8), 2) for o, t in zip(outstanding, tenure_months)]
dpd           = []
for s in [random.choice(LOAN_STATUS) for _ in range(n)]:
    if s == "Default":    dpd.append(random.randint(90, 365))
    elif s == "Watch":    dpd.append(random.randint(31, 89))
    elif s == "Active":   dpd.append(random.randint(0, 30))
    else:                 dpd.append(0)
statuses      = ["Default" if d >= 90 else "Watch" if d >= 31 else "Active" if d > 0 else random.choice(["Active","Closed","Restructured"]) for d in dpd]
credit_scores = [random.randint(450, 850) for _ in range(n)]
collateral    = [random.choice(COLLATERAL) for _ in range(n)]
cities        = [random.choice(CITIES) for _ in range(n)]
segments      = [random.choice(SEGMENTS) for _ in range(n)]
disbursal     = [rand_date("2019-01-01", "2023-12-31") for _ in range(n)]
maturity      = [d + timedelta(days=t*30) for d, t in zip(disbursal, tenure_months)]
risk_grade    = ["A" if cs >= 750 else "B" if cs >= 650 else "C" if cs >= 550 else "D" for cs in credit_scores]

loans_df = pd.DataFrame({
    "loan_id": loan_ids,
    "customer_id": cust_ids,
    "loan_type": loan_types,
    "city": cities,
    "segment": segments,
    "principal_amount": principal,
    "interest_rate_pct": interest_rate,
    "tenure_months": tenure_months,
    "outstanding_balance": outstanding,
    "emi_amount": emi,
    "dpd": dpd,
    "loan_status": statuses,
    "credit_score": credit_scores,
    "risk_grade": risk_grade,
    "collateral_type": collateral,
    "disbursal_date": disbursal,
    "maturity_date": maturity,
})

path = OUT / "Banking_LoanPortfolio.xlsx"
loans_df.to_excel(path, index=False, sheet_name="Loan_Portfolio")
style_wb(path)
print(f"  Saved: {path}  ({len(loans_df)} rows)")


# ══════════════════════════════════════════════════════════════════════════════
# 2. Insurance_Claims.xlsx
# ══════════════════════════════════════════════════════════════════════════════
print("Generating Insurance_Claims.xlsx ...")

CLAIM_TYPES  = ["Motor", "Health", "Property", "Life", "Travel", "Liability"]
REGIONS      = ["North", "South", "East", "West", "Central"]
STATUS_CL    = ["Approved", "Rejected", "Pending", "Under Review", "Settled"]
FRAUD_FLAG   = (["No"]*78 + ["Yes"]*14 + ["Suspected"]*8)
POLICY_TYPES = ["Comprehensive", "Third Party", "Individual", "Family Floater", "Group"]

n = 400
claim_ids    = [f"CLM{i:06d}" for i in range(1, n+1)]
policy_nos   = [f"POL{random.randint(10000,99999)}" for _ in range(n)]
claimant_ids = [f"P{random.randint(1,120):04d}" for _ in range(n)]
claim_types  = [random.choice(CLAIM_TYPES) for _ in range(n)]
policy_types = [random.choice(POLICY_TYPES) for _ in range(n)]
regions      = [random.choice(REGIONS) for _ in range(n)]
claim_dates  = [rand_date("2022-01-01", "2024-12-31") for _ in range(n)]
claim_amounts= [round(random.uniform(1000, 500000), 2) for _ in range(n)]
approved_amt = [round(a * random.uniform(0, 1.0), 2) if random.random() > 0.2 else 0 for a in claim_amounts]
fraud_flags  = [random.choice(FRAUD_FLAG) for _ in range(n)]
# High-amount claims more likely fraud
fraud_flags  = ["Yes" if a > 300000 and random.random() > 0.5 else f for a, f in zip(claim_amounts, fraud_flags)]
statuses_cl  = [random.choice(STATUS_CL) for _ in range(n)]
process_days = [random.randint(1, 90) for _ in range(n)]
# Fraud claims take longer
process_days = [d + random.randint(20, 60) if f == "Yes" else d for d, f in zip(process_days, fraud_flags)]
agent_ids    = [f"AGT{random.randint(1,30):03d}" for _ in range(n)]
num_prior    = [random.randint(0, 8) for _ in range(n)]
# High prior claims → suspect
fraud_flags  = ["Suspected" if p >= 4 and f == "No" else f for p, f in zip(num_prior, fraud_flags)]
settlement   = [d + timedelta(days=pd_) for d, pd_ in zip(claim_dates, process_days)]
ages         = [random.randint(22, 72) for _ in range(n)]
premium_paid = [round(random.uniform(5000, 80000), 2) for _ in range(n)]

claims_df = pd.DataFrame({
    "claim_id": claim_ids,
    "policy_no": policy_nos,
    "claimant_id": claimant_ids,
    "claim_type": claim_types,
    "policy_type": policy_types,
    "region": regions,
    "claimant_age": ages,
    "claim_date": claim_dates,
    "claim_amount": claim_amounts,
    "approved_amount": approved_amt,
    "premium_paid": premium_paid,
    "prior_claims_count": num_prior,
    "claim_status": statuses_cl,
    "fraud_flag": fraud_flags,
    "processing_days": process_days,
    "settlement_date": settlement,
    "agent_id": agent_ids,
})

path = OUT / "Insurance_Claims.xlsx"
claims_df.to_excel(path, index=False, sheet_name="Claims")
style_wb(path)
print(f"  Saved: {path}  ({len(claims_df)} rows)")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Retail_Sales.xlsx  (multi-tab: Sales + Products + Returns)
# ══════════════════════════════════════════════════════════════════════════════
print("Generating Retail_Sales.xlsx ...")

CATEGORIES  = ["Electronics", "Apparel", "Home & Kitchen", "Sports", "Beauty", "Books", "Toys", "Grocery"]
SUB_CATS    = {
    "Electronics": ["Mobile", "Laptop", "Tablet", "Headphones", "Camera"],
    "Apparel":     ["Shirts", "Jeans", "Dresses", "Shoes", "Jackets"],
    "Home & Kitchen": ["Cookware", "Furniture", "Bedding", "Decor", "Appliances"],
    "Sports":      ["Footwear", "Equipment", "Clothing", "Nutrition", "Accessories"],
    "Beauty":      ["Skincare", "Haircare", "Makeup", "Fragrance", "Wellness"],
    "Books":       ["Fiction", "Non-Fiction", "Academic", "Children", "Comics"],
    "Toys":        ["Action", "Educational", "Outdoor", "Board Games", "Dolls"],
    "Grocery":     ["Snacks", "Beverages", "Dairy", "Fresh Produce", "Packaged"],
}
REGIONS_R   = ["North India", "South India", "East India", "West India", "Central India"]
CHANNELS    = ["Online", "Store", "Marketplace", "B2B", "Social Commerce"]
MONTHS      = pd.date_range("2023-01-01", periods=24, freq="MS")

# Products master
products    = []
for pid in range(1, 101):
    cat = random.choice(CATEGORIES)
    sub = random.choice(SUB_CATS[cat])
    products.append({
        "product_id": f"SKU{pid:04d}",
        "product_name": f"{sub} {random.choice(['Pro','Plus','Elite','Basic','Max','Lite'])} {random.randint(100,999)}",
        "category": cat,
        "sub_category": sub,
        "unit_price": round(random.uniform(99, 49999), 2),
        "cost_price": 0,
        "launch_date": rand_date("2020-01-01", "2023-06-30"),
        "brand": random.choice(["AlphaBrand","BetaCo","GammaTech","DeltaStyle","EpsilonFresh"]),
        "stock_units": random.randint(0, 5000),
        "min_stock_level": random.randint(50, 300),
    })
for p in products:
    p["cost_price"] = round(p["unit_price"] * random.uniform(0.35, 0.65), 2)

products_df = pd.DataFrame(products)

# Sales transactions
n = 800
sales = []
for i in range(1, n+1):
    prod = random.choice(products)
    qty  = random.randint(1, 50)
    disc = round(random.uniform(0, 0.35), 2)
    rev  = round(prod["unit_price"] * qty * (1 - disc), 2)
    mth  = random.choice(MONTHS)
    # Seasonal boost: Dec and Jan get higher volumes
    if mth.month in [11, 12, 1]:
        qty = int(qty * random.uniform(1.5, 2.5))
        rev = round(prod["unit_price"] * qty * (1 - disc), 2)
    sales.append({
        "order_id": f"ORD{i:06d}",
        "product_id": prod["product_id"],
        "product_name": prod["product_name"],
        "category": prod["category"],
        "region": random.choice(REGIONS_R),
        "channel": random.choice(CHANNELS),
        "sale_month": mth.strftime("%Y-%m"),
        "sale_date": mth + timedelta(days=random.randint(0, 27)),
        "quantity_sold": qty,
        "unit_price": prod["unit_price"],
        "discount_pct": disc,
        "revenue": rev,
        "profit": round(rev - prod["cost_price"] * qty, 2),
        "customer_segment": random.choice(["New", "Returning", "Loyal", "VIP"]),
    })

sales_df = pd.DataFrame(sales)

# Returns
n_ret = 120
returns = []
sample_orders = random.sample(sales, n_ret)
for o in sample_orders:
    ret_qty = random.randint(1, min(3, o["quantity_sold"]))
    returns.append({
        "return_id": f"RET{random.randint(10000,99999)}",
        "order_id": o["order_id"],
        "product_id": o["product_id"],
        "category": o["category"],
        "return_date": o["sale_date"] + timedelta(days=random.randint(1, 30)),
        "return_qty": ret_qty,
        "return_reason": random.choice(["Defective", "Wrong Item", "Not as Described", "Changed Mind", "Duplicate Order"]),
        "refund_amount": round(o["unit_price"] * ret_qty * (1 - o["discount_pct"]), 2),
        "return_status": random.choice(["Processed", "Pending", "Rejected"]),
    })

returns_df = pd.DataFrame(returns)

path = OUT / "Retail_Sales.xlsx"
with pd.ExcelWriter(path, engine="openpyxl") as writer:
    sales_df.to_excel(writer, index=False, sheet_name="Sales")
    products_df.to_excel(writer, index=False, sheet_name="Products")
    returns_df.to_excel(writer, index=False, sheet_name="Returns")
style_wb(path)
print(f"  Saved: {path}  ({len(sales_df)} sales, {len(products_df)} products, {len(returns_df)} returns)")


# ══════════════════════════════════════════════════════════════════════════════
# 4. HR_Workforce.xlsx  (multi-tab: Employees + Performance + Attrition)
# ══════════════════════════════════════════════════════════════════════════════
print("Generating HR_Workforce.xlsx ...")

DEPARTMENTS  = ["Engineering", "Sales", "HR", "Finance", "Operations", "Marketing", "Legal", "Product", "Support"]
GRADES       = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]
LOCATIONS    = ["Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune", "Kolkata"]
JOB_TITLES   = {
    "Engineering": ["Software Engineer","Senior Engineer","Tech Lead","Architect","VP Engineering"],
    "Sales":       ["Sales Executive","Account Manager","Sales Lead","Sales Director","VP Sales"],
    "HR":          ["HR Associate","HR Manager","HRBP","HR Director","CHRO"],
    "Finance":     ["Analyst","Senior Analyst","Finance Manager","Controller","CFO"],
    "Operations":  ["Ops Associate","Ops Manager","Sr Manager","Director Ops","COO"],
    "Marketing":   ["Marketing Executive","Brand Manager","Digital Lead","Marketing Director","CMO"],
    "Legal":       ["Legal Associate","Legal Manager","Sr Counsel","General Counsel","CLO"],
    "Product":     ["Product Analyst","Product Manager","Sr PM","Group PM","VP Product"],
    "Support":     ["Support Agent","Support Lead","Support Manager","Head of Support","VP CX"],
}
EDUCATION    = ["Bachelor's", "Master's", "MBA", "PhD", "Diploma"]
GENDER       = ["Male", "Female", "Non-Binary"]
ETH          = ["Group A", "Group B", "Group C", "Group D"]

n = 500
emp_ids      = [f"EMP{i:05d}" for i in range(1, n+1)]
depts        = [random.choice(DEPARTMENTS) for _ in range(n)]
grades       = []
salaries     = []
for dept in depts:
    g = random.choices(GRADES, weights=[20,25,20,15,10,6,4])[0]
    grades.append(g)
    base = {"L1":350000,"L2":550000,"L3":800000,"L4":1200000,"L5":1800000,"L6":2500000,"L7":3800000}[g]
    salaries.append(round(base * random.uniform(0.85, 1.25), -3))

titles       = [random.choice(JOB_TITLES[d]) for d in depts]
locations    = [random.choice(LOCATIONS) for _ in range(n)]
ages         = [random.randint(22, 58) for _ in range(n)]
genders      = [random.choice(GENDER) for _ in range(n)]
ethnicities  = [random.choice(ETH) for _ in range(n)]
education    = [random.choice(EDUCATION) for _ in range(n)]
tenure_yrs   = [round(random.uniform(0.1, 20), 1) for _ in range(n)]
join_date    = [date.today() - timedelta(days=int(t*365)) for t in tenure_yrs]
manager_ids  = [f"EMP{random.randint(1,50):05d}" for _ in range(n)]
wfh_days     = [random.randint(0, 5) for _ in range(n)]

# Attrition risk: low tenure + low grade + low engagement → higher risk
attrition_risk = []
for t, g, s in zip(tenure_yrs, grades, salaries):
    base_risk = 0.08
    if t < 1: base_risk += 0.25
    if g in ["L1","L2"] and t < 2: base_risk += 0.15
    if s < 500000: base_risk += 0.10
    attrition_risk.append(min(round(base_risk + random.uniform(-0.05, 0.15), 2), 0.95))

# Pay gap (gender-based)
for i, (g, s) in enumerate(zip(genders, salaries)):
    if g == "Female":
        if random.random() > 0.6:
            salaries[i] = round(s * random.uniform(0.78, 0.95), -3)
    elif g == "Non-Binary":
        if random.random() > 0.5:
            salaries[i] = round(s * random.uniform(0.82, 0.97), -3)

employees_df = pd.DataFrame({
    "employee_id": emp_ids,
    "department": depts,
    "job_title": titles,
    "grade": grades,
    "location": locations,
    "age": ages,
    "gender": genders,
    "ethnicity": ethnicities,
    "education": education,
    "join_date": join_date,
    "tenure_years": tenure_yrs,
    "annual_salary": salaries,
    "wfh_days_per_week": wfh_days,
    "manager_id": manager_ids,
    "attrition_risk_score": attrition_risk,
})

# Performance reviews
perf_records = []
for eid, dept, grade in zip(emp_ids, depts, grades):
    for yr in [2022, 2023, 2024]:
        rating = random.choices([1,2,3,4,5], weights=[5,10,40,30,15])[0]
        # L6/L7 slightly higher ratings
        if grade in ["L6","L7"]: rating = min(5, rating + random.choice([0,0,1]))
        perf_records.append({
            "employee_id": eid,
            "review_year": yr,
            "department": dept,
            "performance_rating": rating,
            "rating_label": {1:"Needs Improvement",2:"Below Expectations",3:"Meets Expectations",4:"Exceeds Expectations",5:"Outstanding"}[rating],
            "goals_met_pct": round(random.uniform(40, 100), 1),
            "training_hours": random.randint(0, 80),
            "promoted": random.choice([True, False, False, False, False]),
            "bonus_pct": round(random.uniform(0, 25), 1) if rating >= 4 else round(random.uniform(0, 8), 1),
        })

perf_df = pd.DataFrame(perf_records)

# Attrition history (left employees)
n_left = 80
attrition_records = []
for i in range(n_left):
    dept = random.choice(DEPARTMENTS)
    g    = random.choices(GRADES, weights=[30,25,20,12,8,3,2])[0]
    sal  = {"L1":350000,"L2":550000,"L3":800000,"L4":1200000,"L5":1800000,"L6":2500000,"L7":3800000}[g]
    ten  = round(random.uniform(0.1, 5), 1)
    attrition_records.append({
        "employee_id": f"EMP_EX{i:04d}",
        "department": dept,
        "grade": g,
        "gender": random.choice(GENDER),
        "location": random.choice(LOCATIONS),
        "tenure_years": ten,
        "annual_salary": round(sal * random.uniform(0.85, 1.1), -3),
        "exit_reason": random.choice(["Better Opportunity","Work-Life Balance","Compensation","Relocation","Personal","Management Issues","Career Growth"]),
        "exit_date": rand_date("2022-01-01", "2024-12-31"),
        "performance_at_exit": random.choice([2,3,3,4,4,5]),
        "notice_period_days": random.choice([30,60,90]),
        "rehire_eligible": random.choice(["Yes","No","Maybe"]),
    })

attrition_df = pd.DataFrame(attrition_records)

path = OUT / "HR_Workforce.xlsx"
with pd.ExcelWriter(path, engine="openpyxl") as writer:
    employees_df.to_excel(writer, index=False, sheet_name="Employees")
    perf_df.to_excel(writer, index=False, sheet_name="Performance")
    attrition_df.to_excel(writer, index=False, sheet_name="Attrition")
style_wb(path)
print(f"  Saved: {path}  ({len(employees_df)} employees, {len(perf_df)} perf rows, {len(attrition_df)} attrition rows)")

print()
print("All 4 use-case datasets saved to:", OUT)
print()
print("Files:")
for f in sorted(OUT.glob("*.xlsx")):
    size_kb = f.stat().st_size // 1024
    print(f"  {f.name:<40} {size_kb} KB")
