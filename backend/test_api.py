import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000/api"

def test_flow():
    print("🚀 Starting API Test Flow...\n")

    # 1. Create Session
    print("1️⃣ Creating Session...")
    res = requests.post(f"{BASE_URL}/sessions")
    res.raise_for_status()
    session_id = res.json()["session_id"]
    print(f"✅ Session Created: {session_id}\n")

    # 2. Upload JD
    print("2️⃣ Uploading Job Description...")
    jd_data = {
        "session_id": session_id,
        "text": "Senior Python Developer at Google. Must have 3+ years Python, FastAPI, Docker, and System Design experience. Nice to have: Kubernetes and CI/CD."
    }
    res = requests.post(f"{BASE_URL}/upload/jd", data=jd_data)
    res.raise_for_status()
    print("✅ JD Parsed Successfully! Found skills:", [s["name"] for s in res.json()["jd_data"]["required_skills"]])
    print("\n")

    # 3. Create a dummy resume text file to test upload
    print("3️⃣ Uploading Resume...")
    with open("dummy_resume.txt", "w") as f:
        f.write("John Doe\nExperienced Backend Engineer.\nSkills: Python (3 years), Flask (2 years), PostgreSQL, basic Docker.\nExperience: Built REST APIs for e-commerce platforms.")
    
    with open("dummy_resume.txt", "rb") as f:
        res = requests.post(f"{BASE_URL}/upload/resume", data={"session_id": session_id}, files={"file": f})
    
    os.remove("dummy_resume.txt")  # cleanup
    res.raise_for_status()
    print("✅ Resume Parsed Successfully! Found skills:", [s["name"] for s in res.json()["resume_data"]["skills"]])
    print("\n")

    # 4. Generate Gap Analysis
    print("4️⃣ Generating Gap Analysis (Calling OpenAI)...")
    res = requests.post(f"{BASE_URL}/analysis/generate", json={"session_id": session_id})
    res.raise_for_status()
    analysis = res.json()["gap_analysis"]
    print(f"✅ Analysis Complete! Overall Match Score: {analysis['overall_match_score']}")
    print(f"   Critical Gaps: {analysis['critical_gaps']}")
    print("\n")

    # 5. Generate Learning Plan
    print("5️⃣ Generating Learning Plan (Calling Tavily Search + OpenAI)...")
    res = requests.post(f"{BASE_URL}/learning-plan/generate", json={"session_id": session_id})
    res.raise_for_status()
    plan = res.json()["learning_plan"]
    print(f"✅ Learning Plan Complete! Total Est Hours: {plan['total_estimated_hours']}")
    print("   Courses Generated:")
    for course in plan["courses"]:
        print(f"    - {course['skill_name']} ({course['gap_category']})")

    print("\n🎉 All Tests Passed Successfully!")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
