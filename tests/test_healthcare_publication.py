import unittest
from pathlib import Path


class TestHealthcarePublicationArtifacts(unittest.TestCase):
    def test_healthcare_article_includes_claim_limits_sources_and_mayo_caveat(self):
        article = Path("docs/articles/decision-pga-healthcare-decision-state-diagnostics.md")
        text = article.read_text(encoding="utf-8")

        self.assertIn("Decision-State Diagnostics for Healthcare AI", text)
        self.assertIn("personal technical perspective, not an institutional statement", text)
        self.assertIn("not clinical validation", text)
        self.assertIn("no patient data", text)
        self.assertIn("not a medical device or clinical decision support product", text)
        self.assertIn("Mayo Clinic", text)
        for link in [
            "https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-aiml-enabled-medical-devices",
            "https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software-frequently-asked-questions-faqs",
            "https://healthit.gov/regulations/hti-rules/hti-1-final-rule/",
            "https://www.who.int/publications/i/item/9789240029200",
            "https://www.mayoclinic.org/giving-to-mayo-clinic/our-priorities/artificial-intelligence",
            "https://www.mayoclinic.org/giving-to-mayo-clinic/our-priorities/mayo-clinic-platform",
        ]:
            self.assertIn(link, text)

    def test_publication_plan_has_one_week_no_cost_path(self):
        plan = Path("docs/healthcare-publication-plan.md")
        text = plan.read_text(encoding="utf-8")

        self.assertIn("One-week publication path", text)
        self.assertIn("GitHub Pages or repository Markdown", text)
        self.assertIn("Substack or Medium", text)
        self.assertIn("OSF Preprints", text)
        self.assertIn("Zenodo", text)
        self.assertIn("arXiv", text)
        self.assertIn("Do not wait for clinical-grade code", text)


if __name__ == "__main__":
    unittest.main()
