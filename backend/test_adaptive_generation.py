import os
import sys
import unittest
import json

# Add parent directory to path to ensure imports work
sys.path.append(os.path.dirname(__file__))

from server import app, get_db, get_complexity_level, adapt_task_locally, generate_ai_tasks

class TestAdaptiveGeneration(unittest.TestCase):
    def test_get_complexity_level(self):
        # Primary: Class 4-6 or Age <= 11
        self.assertEqual(get_complexity_level("Class 4", None), "PRIMARY")
        self.assertEqual(get_complexity_level("Grade 5", None), "PRIMARY")
        self.assertEqual(get_complexity_level("class 6", None), "PRIMARY")
        self.assertEqual(get_complexity_level(None, 10), "PRIMARY")
        self.assertEqual(get_complexity_level(None, 8), "PRIMARY")
        
        # Middle: Class 7-8 or Age 12-13
        self.assertEqual(get_complexity_level("Class 7", None), "MIDDLE")
        self.assertEqual(get_complexity_level("Grade 8", None), "MIDDLE")
        self.assertEqual(get_complexity_level(None, 12), "MIDDLE")
        
        # Secondary: Class 9-10 or Age 14-15
        self.assertEqual(get_complexity_level("Class 9", None), "SECONDARY")
        self.assertEqual(get_complexity_level("Grade 10", None), "SECONDARY")
        self.assertEqual(get_complexity_level(None, 14), "SECONDARY")
        
        # Senior: Class 11-12 or Age 16-18
        self.assertEqual(get_complexity_level("Class 11", None), "SENIOR")
        self.assertEqual(get_complexity_level("Grade 12", None), "SENIOR")
        self.assertEqual(get_complexity_level(None, 17), "SENIOR")
        
        # Fallback
        self.assertEqual(get_complexity_level("", ""), "MIDDLE")
        self.assertEqual(get_complexity_level("invalid", "invalid"), "MIDDLE")

    def test_adapt_task_locally_primary(self):
        # Test override match for primary level
        task_pattern = {
            "key": "logical_pattern_matrix",
            "title": {"English": "Pattern Matrix", "Hindi": "पैटर्न"},
            "prompt": {"English": "Original English prompt", "Hindi": "मूल हिंदी प्रॉम्प्ट"},
            "domain": "logical"
        }
        
        adapted_en = adapt_task_locally(task_pattern, "PRIMARY", "English")
        self.assertEqual(adapted_en["title"], "The Magic Lock")
        self.assertIn("Add numbers to open the lock", adapted_en["prompt"])
        
        adapted_hi = adapt_task_locally(task_pattern, "PRIMARY", "Hindi")
        self.assertEqual(adapted_hi["title"], "जादू की संख्या")
        self.assertIn("ताला खोलने के लिए संख्याओं को जोड़ें", adapted_hi["prompt"])
        
        # Test fallback regex matching when no override is present
        task_fallback = {
            "key": "random_key",
            "title": {"English": "My Leadership Task", "Hindi": "नेतृत्व कार्य"},
            "prompt": {"English": "This measures your leadership and resilience.", "Hindi": "यह आपके नेतृत्व और लचीलेपन को मापता है।"},
            "domain": "social"
        }
        adapted_fb = adapt_task_locally(task_fallback, "PRIMARY", "English")
        # should replace "leadership" with "group planning" and "resilience" with "strength"
        self.assertNotIn("leadership", adapted_fb["prompt"].lower())
        self.assertNotIn("resilience", adapted_fb["prompt"].lower())
        self.assertIn("group planning", adapted_fb["prompt"].lower())
        self.assertIn("strength", adapted_fb["prompt"].lower())
        # should add emoji 🌟 since none of the specified emojis were present
        self.assertIn("🌟", adapted_fb["prompt"])

    def test_adapt_task_locally_advanced(self):
        task_pattern = {
            "key": "logical_pattern_matrix",
            "title": {"English": "Pattern Matrix", "Hindi": "पैटर्न"},
            "prompt": {"English": "Original English prompt", "Hindi": "मूल हिंदी प्रॉम्प्ट"},
            "domain": "logical"
        }
        
        # Secondary level overrides
        adapted_sec = adapt_task_locally(task_pattern, "SECONDARY", "English")
        self.assertEqual(adapted_sec["title"], "The Numerical Matrix Crypt")
        self.assertIn("Analyze the sequence hierarchy", adapted_sec["prompt"])
        
        # Senior level overrides
        adapted_sen = adapt_task_locally(task_pattern, "SENIOR", "Hindi")
        self.assertEqual(adapted_sen["title"], "संख्यात्मक मैट्रिक्स")
        self.assertIn("संख्यात्मक मैट्रिक्स में अनुक्रम पदानुक्रम का विश्लेषण करें", adapted_sen["prompt"])

    def test_generate_ai_tasks_integration(self):
        with app.app_context():
            # Create a child in memory or get one
            db = get_db()
            child_row = db.execute("SELECT * FROM children LIMIT 1").fetchone()
            if not child_row:
                db.execute("INSERT INTO children (name, age, school_year, language) VALUES ('Test Student', 9, 'Class 4', 'English')")
                db.commit()
                child_row = db.execute("SELECT * FROM children LIMIT 1").fetchone()
            
            child = dict(child_row)
            # Override for primary test
            child["school_year"] = "Class 4"
            child["age"] = 9
            child["language"] = "English"
            
            discovery_answers = {
                "q_discovery_1": 0, # logical
                "q_discovery_2": 0, # spatial
                "q_discovery_3": 0, # naturalist
                "q_discovery_4": 0, # social
                "q_discovery_5": 0, # logical
                "q_discovery_6": 0, # creative
                "q_discovery_7": 0, # naturalist
                "q_discovery_8": 0, # language
                "q_discovery_9": 0, # naturalist
                "q_discovery_10": 0, # kinesthetic
                "q_discovery_11": 0, # naturalist
                "q_discovery_12": 0  # logical
            }
            
            tasks = generate_ai_tasks(child, discovery_answers)
            self.assertTrue(len(tasks) > 0)
            
            # Check that keys are preserved and adapted
            for task in tasks:
                self.assertIn("key", task)
                self.assertIn("domain", task)
                self.assertIn("title", task)
                self.assertIn("prompt", task)
                # Verify that title and prompt are strings (not dicts, since they are adapted to target language)
                self.assertIsInstance(task["title"], str)
                self.assertIsInstance(task["prompt"], str)
                
                # Check that primary adaptation is applied
                if task["key"] == "logical_pattern_matrix":
                    self.assertEqual(task["title"], "The Magic Lock")
                    self.assertIn("Add numbers to open the lock", task["prompt"])

if __name__ == "__main__":
    unittest.main()
