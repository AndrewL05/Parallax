"""
Profession-Specific Salary and Career Data

Centralized data for profession-specific salary ranges, training trajectories,
and career field mappings. Used by ML prediction services for accurate projections.
"""

from typing import Dict, Optional, Tuple, List
from models.ml_models import CareerField


# Profession-specific salary ranges by position level (USD)
# Levels: entry, mid, senior, lead, executive
PROFESSION_SALARIES: Dict[str, Dict[str, int]] = {
    # Healthcare - Physicians & Specialists
    "doctor": {"entry": 62000, "mid": 230000, "senior": 280000, "lead": 350000, "executive": 450000},
    "physician": {"entry": 62000, "mid": 230000, "senior": 280000, "lead": 350000, "executive": 450000},
    "surgeon": {"entry": 65000, "mid": 380000, "senior": 450000, "lead": 520000, "executive": 600000},
    "anesthesiologist": {"entry": 65000, "mid": 350000, "senior": 420000, "lead": 480000, "executive": 550000},
    "psychiatrist": {"entry": 62000, "mid": 250000, "senior": 300000, "lead": 350000, "executive": 400000},
    "cardiologist": {"entry": 65000, "mid": 400000, "senior": 480000, "lead": 550000, "executive": 650000},
    "dermatologist": {"entry": 62000, "mid": 350000, "senior": 420000, "lead": 480000, "executive": 550000},
    "radiologist": {"entry": 65000, "mid": 380000, "senior": 450000, "lead": 500000, "executive": 580000},
    "orthopedic surgeon": {"entry": 65000, "mid": 500000, "senior": 580000, "lead": 650000, "executive": 750000},

    # Healthcare - Other
    "dentist": {"entry": 130000, "mid": 180000, "senior": 220000, "lead": 280000, "executive": 350000},
    "pharmacist": {"entry": 120000, "mid": 135000, "senior": 150000, "lead": 170000, "executive": 200000},
    "nurse": {"entry": 58000, "mid": 75000, "senior": 92000, "lead": 110000, "executive": 140000},
    "nurse practitioner": {"entry": 95000, "mid": 115000, "senior": 130000, "lead": 145000, "executive": 165000},
    "physician assistant": {"entry": 100000, "mid": 120000, "senior": 135000, "lead": 150000, "executive": 175000},
    "physical therapist": {"entry": 70000, "mid": 85000, "senior": 95000, "lead": 110000, "executive": 130000},
    "veterinarian": {"entry": 90000, "mid": 110000, "senior": 130000, "lead": 160000, "executive": 200000},

    # Technology
    "software engineer": {"entry": 85000, "mid": 130000, "senior": 175000, "lead": 230000, "executive": 350000},
    "software developer": {"entry": 80000, "mid": 120000, "senior": 160000, "lead": 210000, "executive": 300000},
    "data scientist": {"entry": 95000, "mid": 140000, "senior": 180000, "lead": 240000, "executive": 350000},
    "data engineer": {"entry": 90000, "mid": 135000, "senior": 175000, "lead": 220000, "executive": 300000},
    "machine learning engineer": {"entry": 100000, "mid": 150000, "senior": 200000, "lead": 270000, "executive": 400000},
    "devops engineer": {"entry": 85000, "mid": 125000, "senior": 165000, "lead": 210000, "executive": 280000},
    "cloud engineer": {"entry": 90000, "mid": 130000, "senior": 170000, "lead": 220000, "executive": 300000},
    "frontend developer": {"entry": 75000, "mid": 110000, "senior": 145000, "lead": 190000, "executive": 260000},
    "backend developer": {"entry": 80000, "mid": 120000, "senior": 160000, "lead": 210000, "executive": 290000},
    "full stack developer": {"entry": 80000, "mid": 120000, "senior": 160000, "lead": 210000, "executive": 290000},
    "mobile developer": {"entry": 80000, "mid": 120000, "senior": 160000, "lead": 200000, "executive": 280000},
    "cybersecurity engineer": {"entry": 85000, "mid": 125000, "senior": 165000, "lead": 210000, "executive": 300000},
    "security analyst": {"entry": 75000, "mid": 100000, "senior": 130000, "lead": 165000, "executive": 220000},
    "product manager": {"entry": 90000, "mid": 130000, "senior": 170000, "lead": 220000, "executive": 320000},
    "engineering manager": {"entry": 130000, "mid": 170000, "senior": 210000, "lead": 260000, "executive": 380000},
    "cto": {"entry": 180000, "mid": 250000, "senior": 320000, "lead": 400000, "executive": 550000},

    # Finance & Business
    "investment banker": {"entry": 120000, "mid": 200000, "senior": 350000, "lead": 500000, "executive": 1000000},
    "financial analyst": {"entry": 65000, "mid": 85000, "senior": 110000, "lead": 145000, "executive": 200000},
    "accountant": {"entry": 55000, "mid": 72000, "senior": 90000, "lead": 120000, "executive": 180000},
    "cpa": {"entry": 60000, "mid": 80000, "senior": 105000, "lead": 140000, "executive": 220000},
    "actuary": {"entry": 75000, "mid": 120000, "senior": 160000, "lead": 220000, "executive": 350000},
    "financial advisor": {"entry": 50000, "mid": 85000, "senior": 130000, "lead": 200000, "executive": 350000},
    "hedge fund manager": {"entry": 150000, "mid": 350000, "senior": 600000, "lead": 1000000, "executive": 2000000},
    "venture capitalist": {"entry": 120000, "mid": 250000, "senior": 450000, "lead": 750000, "executive": 1500000},
    "management consultant": {"entry": 85000, "mid": 140000, "senior": 200000, "lead": 300000, "executive": 500000},
    "strategy consultant": {"entry": 90000, "mid": 150000, "senior": 220000, "lead": 350000, "executive": 550000},

    # Legal
    "lawyer": {"entry": 95000, "mid": 160000, "senior": 250000, "lead": 400000, "executive": 700000},
    "attorney": {"entry": 95000, "mid": 160000, "senior": 250000, "lead": 400000, "executive": 700000},
    "corporate lawyer": {"entry": 120000, "mid": 200000, "senior": 350000, "lead": 550000, "executive": 1000000},
    "patent attorney": {"entry": 130000, "mid": 200000, "senior": 300000, "lead": 450000, "executive": 700000},
    "paralegal": {"entry": 45000, "mid": 58000, "senior": 72000, "lead": 85000, "executive": 100000},

    # Engineering (Non-Software)
    "mechanical engineer": {"entry": 68000, "mid": 90000, "senior": 115000, "lead": 145000, "executive": 200000},
    "electrical engineer": {"entry": 72000, "mid": 95000, "senior": 120000, "lead": 150000, "executive": 210000},
    "civil engineer": {"entry": 65000, "mid": 85000, "senior": 105000, "lead": 135000, "executive": 180000},
    "chemical engineer": {"entry": 75000, "mid": 100000, "senior": 130000, "lead": 165000, "executive": 220000},
    "aerospace engineer": {"entry": 75000, "mid": 105000, "senior": 135000, "lead": 170000, "executive": 230000},
    "biomedical engineer": {"entry": 65000, "mid": 90000, "senior": 115000, "lead": 145000, "executive": 200000},
    "petroleum engineer": {"entry": 85000, "mid": 130000, "senior": 175000, "lead": 220000, "executive": 300000},
    "architect": {"entry": 55000, "mid": 80000, "senior": 105000, "lead": 140000, "executive": 200000},

    # Education
    "teacher": {"entry": 45000, "mid": 55000, "senior": 68000, "lead": 82000, "executive": 100000},
    "professor": {"entry": 70000, "mid": 95000, "senior": 130000, "lead": 170000, "executive": 250000},
    "principal": {"entry": 85000, "mid": 105000, "senior": 125000, "lead": 145000, "executive": 175000},
    "school counselor": {"entry": 48000, "mid": 58000, "senior": 70000, "lead": 82000, "executive": 95000},

    # Creative & Media
    "graphic designer": {"entry": 45000, "mid": 62000, "senior": 82000, "lead": 105000, "executive": 150000},
    "ux designer": {"entry": 70000, "mid": 100000, "senior": 135000, "lead": 175000, "executive": 240000},
    "ui designer": {"entry": 65000, "mid": 90000, "senior": 120000, "lead": 155000, "executive": 210000},
    "product designer": {"entry": 75000, "mid": 110000, "senior": 150000, "lead": 195000, "executive": 280000},
    "art director": {"entry": 65000, "mid": 95000, "senior": 130000, "lead": 170000, "executive": 230000},
    "marketing manager": {"entry": 60000, "mid": 85000, "senior": 115000, "lead": 155000, "executive": 220000},
    "copywriter": {"entry": 45000, "mid": 62000, "senior": 80000, "lead": 100000, "executive": 140000},
    "journalist": {"entry": 40000, "mid": 55000, "senior": 75000, "lead": 100000, "executive": 150000},
    "video editor": {"entry": 42000, "mid": 58000, "senior": 78000, "lead": 100000, "executive": 140000},
    "photographer": {"entry": 35000, "mid": 50000, "senior": 70000, "lead": 95000, "executive": 140000},

    # Trades & Technical
    "electrician": {"entry": 45000, "mid": 60000, "senior": 78000, "lead": 95000, "executive": 120000},
    "plumber": {"entry": 42000, "mid": 58000, "senior": 75000, "lead": 92000, "executive": 115000},
    "hvac technician": {"entry": 40000, "mid": 55000, "senior": 72000, "lead": 88000, "executive": 110000},
    "welder": {"entry": 40000, "mid": 52000, "senior": 68000, "lead": 85000, "executive": 105000},
    "pilot": {"entry": 70000, "mid": 130000, "senior": 200000, "lead": 280000, "executive": 400000},

    # Service & Hospitality
    "chef": {"entry": 35000, "mid": 52000, "senior": 75000, "lead": 100000, "executive": 150000},
    "executive chef": {"entry": 60000, "mid": 85000, "senior": 110000, "lead": 140000, "executive": 200000},
    "restaurant manager": {"entry": 45000, "mid": 58000, "senior": 75000, "lead": 95000, "executive": 130000},
    "hotel manager": {"entry": 50000, "mid": 70000, "senior": 95000, "lead": 130000, "executive": 200000},

    # Science & Research
    "research scientist": {"entry": 65000, "mid": 90000, "senior": 120000, "lead": 155000, "executive": 220000},
    "biologist": {"entry": 50000, "mid": 70000, "senior": 95000, "lead": 125000, "executive": 175000},
    "chemist": {"entry": 55000, "mid": 75000, "senior": 100000, "lead": 130000, "executive": 180000},
    "physicist": {"entry": 70000, "mid": 100000, "senior": 135000, "lead": 175000, "executive": 250000},

    # Government & Public Sector
    "police officer": {"entry": 50000, "mid": 65000, "senior": 82000, "lead": 100000, "executive": 130000},
    "firefighter": {"entry": 48000, "mid": 62000, "senior": 78000, "lead": 95000, "executive": 120000},
    "social worker": {"entry": 42000, "mid": 52000, "senior": 65000, "lead": 78000, "executive": 95000},

    # Real Estate
    "real estate agent": {"entry": 40000, "mid": 75000, "senior": 120000, "lead": 200000, "executive": 400000},
    "real estate broker": {"entry": 60000, "mid": 110000, "senior": 180000, "lead": 300000, "executive": 600000},

    # Human Resources
    "hr manager": {"entry": 60000, "mid": 80000, "senior": 105000, "lead": 135000, "executive": 200000},
    "recruiter": {"entry": 45000, "mid": 62000, "senior": 82000, "lead": 105000, "executive": 150000},
}


# Careers with training/residency periods before reaching full salary
# training_years: Years at lower salary before jumping to post_training salary
TRAINING_CAREERS: Dict[str, Dict[str, any]] = {
    "doctor": {
        "training_years": 4,  # Residency
        "training_salary": 62000,
        "post_training_salary": 230000,
        "annual_training_raise": 0.03
    },
    "physician": {
        "training_years": 4,
        "training_salary": 62000,
        "post_training_salary": 230000,
        "annual_training_raise": 0.03
    },
    "surgeon": {
        "training_years": 7,  # Longer residency + fellowship
        "training_salary": 65000,
        "post_training_salary": 380000,
        "annual_training_raise": 0.03
    },
    "anesthesiologist": {
        "training_years": 5,
        "training_salary": 65000,
        "post_training_salary": 350000,
        "annual_training_raise": 0.03
    },
    "cardiologist": {
        "training_years": 7,
        "training_salary": 65000,
        "post_training_salary": 400000,
        "annual_training_raise": 0.03
    },
    "dermatologist": {
        "training_years": 5,
        "training_salary": 62000,
        "post_training_salary": 350000,
        "annual_training_raise": 0.03
    },
    "radiologist": {
        "training_years": 6,
        "training_salary": 65000,
        "post_training_salary": 380000,
        "annual_training_raise": 0.03
    },
    "psychiatrist": {
        "training_years": 5,
        "training_salary": 62000,
        "post_training_salary": 250000,
        "annual_training_raise": 0.03
    },
    "orthopedic surgeon": {
        "training_years": 8,
        "training_salary": 65000,
        "post_training_salary": 500000,
        "annual_training_raise": 0.03
    },
}


# Map professions to career fields
PROFESSION_TO_FIELD: Dict[str, CareerField] = {
    # Healthcare
    "doctor": CareerField.HEALTHCARE,
    "physician": CareerField.HEALTHCARE,
    "surgeon": CareerField.HEALTHCARE,
    "anesthesiologist": CareerField.HEALTHCARE,
    "psychiatrist": CareerField.HEALTHCARE,
    "cardiologist": CareerField.HEALTHCARE,
    "dermatologist": CareerField.HEALTHCARE,
    "radiologist": CareerField.HEALTHCARE,
    "orthopedic surgeon": CareerField.HEALTHCARE,
    "dentist": CareerField.HEALTHCARE,
    "pharmacist": CareerField.HEALTHCARE,
    "nurse": CareerField.HEALTHCARE,
    "nurse practitioner": CareerField.HEALTHCARE,
    "physician assistant": CareerField.HEALTHCARE,
    "physical therapist": CareerField.HEALTHCARE,
    "veterinarian": CareerField.HEALTHCARE,

    # Technology
    "software engineer": CareerField.TECHNOLOGY,
    "software developer": CareerField.TECHNOLOGY,
    "data scientist": CareerField.TECHNOLOGY,
    "data engineer": CareerField.TECHNOLOGY,
    "machine learning engineer": CareerField.TECHNOLOGY,
    "devops engineer": CareerField.TECHNOLOGY,
    "cloud engineer": CareerField.TECHNOLOGY,
    "frontend developer": CareerField.TECHNOLOGY,
    "backend developer": CareerField.TECHNOLOGY,
    "full stack developer": CareerField.TECHNOLOGY,
    "mobile developer": CareerField.TECHNOLOGY,
    "cybersecurity engineer": CareerField.TECHNOLOGY,
    "security analyst": CareerField.TECHNOLOGY,
    "product manager": CareerField.TECHNOLOGY,
    "engineering manager": CareerField.TECHNOLOGY,
    "cto": CareerField.TECHNOLOGY,

    # Finance
    "investment banker": CareerField.FINANCE,
    "financial analyst": CareerField.FINANCE,
    "accountant": CareerField.FINANCE,
    "cpa": CareerField.FINANCE,
    "actuary": CareerField.FINANCE,
    "financial advisor": CareerField.FINANCE,
    "hedge fund manager": CareerField.FINANCE,
    "venture capitalist": CareerField.FINANCE,

    # Business
    "management consultant": CareerField.BUSINESS,
    "strategy consultant": CareerField.BUSINESS,
    "lawyer": CareerField.BUSINESS,
    "attorney": CareerField.BUSINESS,
    "corporate lawyer": CareerField.BUSINESS,
    "patent attorney": CareerField.BUSINESS,
    "paralegal": CareerField.BUSINESS,
    "hr manager": CareerField.BUSINESS,
    "recruiter": CareerField.BUSINESS,
    "marketing manager": CareerField.BUSINESS,
    "real estate agent": CareerField.BUSINESS,
    "real estate broker": CareerField.BUSINESS,

    # Engineering
    "mechanical engineer": CareerField.ENGINEERING,
    "electrical engineer": CareerField.ENGINEERING,
    "civil engineer": CareerField.ENGINEERING,
    "chemical engineer": CareerField.ENGINEERING,
    "aerospace engineer": CareerField.ENGINEERING,
    "biomedical engineer": CareerField.ENGINEERING,
    "petroleum engineer": CareerField.ENGINEERING,
    "architect": CareerField.ENGINEERING,

    # Education
    "teacher": CareerField.EDUCATION,
    "professor": CareerField.EDUCATION,
    "principal": CareerField.EDUCATION,
    "school counselor": CareerField.EDUCATION,

    # Creative
    "graphic designer": CareerField.CREATIVE,
    "ux designer": CareerField.CREATIVE,
    "ui designer": CareerField.CREATIVE,
    "product designer": CareerField.CREATIVE,
    "art director": CareerField.CREATIVE,
    "copywriter": CareerField.CREATIVE,
    "journalist": CareerField.CREATIVE,
    "video editor": CareerField.CREATIVE,
    "photographer": CareerField.CREATIVE,

    # Service
    "chef": CareerField.SERVICE,
    "executive chef": CareerField.SERVICE,
    "restaurant manager": CareerField.SERVICE,
    "hotel manager": CareerField.SERVICE,
    "electrician": CareerField.SERVICE,
    "plumber": CareerField.SERVICE,
    "hvac technician": CareerField.SERVICE,
    "welder": CareerField.SERVICE,
    "pilot": CareerField.SERVICE,
    "police officer": CareerField.SERVICE,
    "firefighter": CareerField.SERVICE,
    "social worker": CareerField.SERVICE,

    # Science
    "research scientist": CareerField.OTHER,
    "biologist": CareerField.OTHER,
    "chemist": CareerField.OTHER,
    "physicist": CareerField.OTHER,
}


# Keywords for detecting professions from free-text input
PROFESSION_KEYWORDS: Dict[str, List[str]] = {
    "doctor": ["doctor", "md", "medical doctor", "physician"],
    "physician": ["physician"],
    "surgeon": ["surgeon", "surgery"],
    "nurse": ["nurse", "rn", "registered nurse", "nursing"],
    "nurse practitioner": ["nurse practitioner", "np", "arnp"],
    "dentist": ["dentist", "dental", "dds", "dmd"],
    "pharmacist": ["pharmacist", "pharmacy"],
    "software engineer": ["software engineer", "swe", "software engineering"],
    "software developer": ["software developer", "programmer", "coder", "developer"],
    "data scientist": ["data scientist", "data science", "ml scientist"],
    "data engineer": ["data engineer", "data engineering"],
    "machine learning engineer": ["machine learning engineer", "ml engineer", "ai engineer"],
    "lawyer": ["lawyer", "attorney", "law", "legal"],
    "corporate lawyer": ["corporate lawyer", "corporate attorney", "biglaw"],
    "investment banker": ["investment banker", "investment banking", "ib analyst", "ibanker"],
    "financial analyst": ["financial analyst", "finance analyst"],
    "accountant": ["accountant", "accounting", "bookkeeper"],
    "teacher": ["teacher", "teaching", "educator"],
    "professor": ["professor", "academic", "faculty"],
    "mechanical engineer": ["mechanical engineer", "mechanical engineering"],
    "electrical engineer": ["electrical engineer", "ee", "electrical engineering"],
    "civil engineer": ["civil engineer", "civil engineering"],
    "ux designer": ["ux designer", "ux design", "user experience"],
    "product designer": ["product designer", "product design"],
    "graphic designer": ["graphic designer", "graphic design"],
    "marketing manager": ["marketing manager", "marketing director", "head of marketing"],
    "chef": ["chef", "cook", "culinary"],
    "pilot": ["pilot", "airline pilot", "commercial pilot"],
    "police officer": ["police officer", "cop", "law enforcement", "police"],
    "firefighter": ["firefighter", "fire fighter", "fireman"],
    "real estate agent": ["real estate agent", "realtor", "real estate"],
}


def detect_profession(title: str, description: str = "") -> Optional[str]:
    """
    Detect a specific profession from title and description text.

    Args:
        title: Job/career title entered by user
        description: Optional description text

    Returns:
        Matched profession key or None if no match found
    """
    combined_text = f"{title} {description}".lower()

    # Check exact profession matches first (longer matches take priority)
    sorted_professions = sorted(PROFESSION_SALARIES.keys(), key=len, reverse=True)
    for profession in sorted_professions:
        if profession in combined_text:
            return profession

    # Check keyword matches
    for profession, keywords in PROFESSION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in combined_text:
                return profession

    return None


def get_profession_salary(profession: str, position_level: str = "entry") -> Optional[int]:
    """
    Get salary for a specific profession and level.

    Args:
        profession: Profession key
        position_level: entry, mid, senior, lead, or executive

    Returns:
        Salary amount or None if profession not found
    """
    if profession not in PROFESSION_SALARIES:
        return None
    return PROFESSION_SALARIES[profession].get(position_level)


def get_profession_field(profession: str) -> CareerField:
    """
    Get the career field for a profession.

    Args:
        profession: Profession key

    Returns:
        CareerField enum value
    """
    return PROFESSION_TO_FIELD.get(profession, CareerField.OTHER)


def get_training_config(profession: str) -> Optional[Dict]:
    """
    Get training/residency configuration for careers with delayed earning.

    Args:
        profession: Profession key

    Returns:
        Training config dict or None if no training period
    """
    return TRAINING_CAREERS.get(profession)


def calculate_training_salary(profession: str, year_offset: int) -> Optional[Tuple[float, bool]]:
    """
    Calculate salary considering training period for applicable careers.

    Args:
        profession: Profession key
        year_offset: Years since starting career (0 = first year)

    Returns:
        Tuple of (salary, is_in_training) or None if not a training career
    """
    config = get_training_config(profession)
    if not config:
        return None

    training_years = config["training_years"]

    if year_offset < training_years:
        # Still in training (residency, etc.)
        annual_raise = config.get("annual_training_raise", 0.03)
        salary = config["training_salary"] * ((1 + annual_raise) ** year_offset)
        return (salary, True)
    else:
        # Post-training - now earning full salary
        years_post_training = year_offset - training_years
        post_salary = config["post_training_salary"]
        # 5% annual growth after training
        salary = post_salary * ((1.05) ** years_post_training)
        return (salary, False)


# =============================================================================
# Title Generation Functions
# =============================================================================

# Training career title progressions
TRAINING_CAREER_TITLES: Dict[str, Dict[str, List[str]]] = {
    "doctor": {
        "training": ["Resident Physician (PGY-1)", "Resident Physician (PGY-2)",
                    "Resident Physician (PGY-3)", "Chief Resident"],
        "post": ["Attending Physician", "Senior Attending", "Department Head",
                "Chief of Medicine", "Chief Medical Officer"]
    },
    "physician": {
        "training": ["Resident Physician (PGY-1)", "Resident Physician (PGY-2)",
                    "Resident Physician (PGY-3)", "Chief Resident"],
        "post": ["Attending Physician", "Senior Attending", "Department Head",
                "Chief of Medicine", "Chief Medical Officer"]
    },
    "surgeon": {
        "training": ["Surgical Intern", "Surgical Resident (PGY-2)", "Surgical Resident (PGY-3)",
                    "Surgical Resident (PGY-4)", "Surgical Resident (PGY-5)",
                    "Chief Surgical Resident", "Surgical Fellow"],
        "post": ["Attending Surgeon", "Senior Surgeon", "Chief of Surgery",
                "Surgical Director", "Chief Medical Officer"]
    },
    "anesthesiologist": {
        "training": ["Anesthesia Resident (CA-1)", "Anesthesia Resident (CA-2)",
                    "Anesthesia Resident (CA-3)", "Chief Resident", "Fellow"],
        "post": ["Attending Anesthesiologist", "Senior Anesthesiologist",
                "Chief of Anesthesia", "Department Chair", "CMO"]
    },
    "cardiologist": {
        "training": ["Internal Medicine Resident", "IM Resident (PGY-2)", "IM Resident (PGY-3)",
                    "Cardiology Fellow (Year 1)", "Cardiology Fellow (Year 2)",
                    "Cardiology Fellow (Year 3)", "Chief Fellow"],
        "post": ["Attending Cardiologist", "Senior Cardiologist", "Director of Cardiology",
                "Chief of Cardiology", "Chief Medical Officer"]
    },
    "psychiatrist": {
        "training": ["Psychiatry Resident (PGY-1)", "Psychiatry Resident (PGY-2)",
                    "Psychiatry Resident (PGY-3)", "Psychiatry Resident (PGY-4)", "Chief Resident"],
        "post": ["Attending Psychiatrist", "Senior Psychiatrist", "Chief of Psychiatry",
                "Department Chair", "Chief Medical Officer"]
    },
}

# Non-training profession title progressions
PROFESSION_TITLE_PROGRESSIONS: Dict[str, List[str]] = {
    "software engineer": ["Software Engineer I", "Software Engineer II", "Senior Software Engineer",
                         "Staff Engineer", "Principal Engineer"],
    "software developer": ["Developer I", "Developer II", "Senior Developer",
                          "Lead Developer", "Principal Developer"],
    "data scientist": ["Data Scientist I", "Data Scientist II", "Senior Data Scientist",
                      "Staff Data Scientist", "Principal Data Scientist"],
    "nurse": ["Registered Nurse", "Registered Nurse", "Senior RN",
             "Charge Nurse", "Nurse Manager"],
    "teacher": ["Teacher", "Teacher", "Senior Teacher",
               "Department Head", "Assistant Principal"],
    "accountant": ["Staff Accountant", "Accountant", "Senior Accountant",
                  "Accounting Manager", "Controller"],
    "lawyer": ["Associate Attorney", "Associate Attorney", "Senior Associate",
              "Counsel", "Partner"],
    "attorney": ["Associate Attorney", "Associate Attorney", "Senior Associate",
                "Counsel", "Partner"],
    "investment banker": ["Analyst", "Associate", "Vice President",
                         "Director", "Managing Director"],
    "financial analyst": ["Financial Analyst I", "Financial Analyst II", "Senior Financial Analyst",
                         "Finance Manager", "Director of Finance"],
    "marketing manager": ["Marketing Coordinator", "Marketing Specialist", "Marketing Manager",
                         "Senior Marketing Manager", "Director of Marketing"],
}

# Default title progression for unknown professions
DEFAULT_TITLE_PROGRESSION = ["Associate", "Specialist", "Senior Specialist", "Manager", "Director"]


def get_training_career_title(profession: str, year_offset: int, training_config: Dict = None) -> str:
    """
    Generate appropriate title for careers with training periods.

    Args:
        profession: Profession key
        year_offset: Years since starting career
        training_config: Optional training config (will fetch if not provided)

    Returns:
        Appropriate job title for this year
    """
    if training_config is None:
        training_config = get_training_config(profession)

    if not training_config:
        return DEFAULT_TITLE_PROGRESSION[min(year_offset // 2, len(DEFAULT_TITLE_PROGRESSION) - 1)]

    training_years = training_config["training_years"]
    titles = TRAINING_CAREER_TITLES.get(profession.lower())

    if not titles:
        # Default medical training titles
        if year_offset < training_years:
            return f"Resident (Year {year_offset + 1})"
        else:
            years_post = year_offset - training_years
            post_titles = ["Attending", "Senior Attending", "Department Head", "Director", "Chief"]
            return post_titles[min(years_post // 2, len(post_titles) - 1)]

    if year_offset < training_years:
        idx = min(year_offset, len(titles["training"]) - 1)
        return titles["training"][idx]
    else:
        years_post = year_offset - training_years
        idx = min(years_post // 2, len(titles["post"]) - 1)
        return titles["post"][idx]


def get_profession_title(profession: str, year_offset: int) -> str:
    """
    Generate appropriate title for non-training professions based on year.

    Args:
        profession: Profession key
        year_offset: Years since starting career

    Returns:
        Appropriate job title for this year
    """
    titles = PROFESSION_TITLE_PROGRESSIONS.get(profession.lower())
    if titles:
        # Map year to title index (roughly 2 years per level)
        idx = min(year_offset // 2, len(titles) - 1)
        return titles[idx]

    # Default progression for unknown professions
    idx = min(year_offset // 2, len(DEFAULT_TITLE_PROGRESSION) - 1)
    return DEFAULT_TITLE_PROGRESSION[idx]


def get_profession_titles_by_level(profession: str) -> Optional[Dict[str, str]]:
    """
    Get position titles for non-training professions mapped by level.

    Args:
        profession: Profession key

    Returns:
        Dict mapping position levels to titles, or None if not defined
    """
    level_mapping = {
        "software engineer": {
            "entry": "Software Engineer I",
            "mid": "Software Engineer II",
            "senior": "Senior Software Engineer",
            "lead": "Staff Engineer",
            "executive": "Principal Engineer"
        },
        "data scientist": {
            "entry": "Data Scientist I",
            "mid": "Data Scientist II",
            "senior": "Senior Data Scientist",
            "lead": "Staff Data Scientist",
            "executive": "Principal Data Scientist"
        },
        "lawyer": {
            "entry": "Associate Attorney",
            "mid": "Senior Associate",
            "senior": "Counsel",
            "lead": "Partner",
            "executive": "Managing Partner"
        },
        "attorney": {
            "entry": "Associate Attorney",
            "mid": "Senior Associate",
            "senior": "Counsel",
            "lead": "Partner",
            "executive": "Managing Partner"
        },
        "investment banker": {
            "entry": "Analyst",
            "mid": "Associate",
            "senior": "Vice President",
            "lead": "Director",
            "executive": "Managing Director"
        },
        "teacher": {
            "entry": "Teacher",
            "mid": "Senior Teacher",
            "senior": "Department Head",
            "lead": "Assistant Principal",
            "executive": "Principal"
        },
        "nurse": {
            "entry": "Registered Nurse",
            "mid": "Senior RN",
            "senior": "Charge Nurse",
            "lead": "Nurse Manager",
            "executive": "Director of Nursing"
        },
        "accountant": {
            "entry": "Staff Accountant",
            "mid": "Senior Accountant",
            "senior": "Accounting Manager",
            "lead": "Controller",
            "executive": "CFO"
        },
    }

    return level_mapping.get(profession.lower())
