from src.scraper.category_filter import classify_product_category


ACCESSORIES = [
    "Redragon RANGER Wired Gaming Mouse High Precision USB Mouse for PC Laptop",
    "Power Adaptor Charger Laptop INNERGIE Gaming Universal",
    "Team Elite 16GB DDR4 Sodimm Ram For Laptop Gaming",
    "Mouse Pad Gaming Anime Extra Large Alas Mouse Laptop",
    "Fantech Webcam C50 for Computer PC Laptop Gaming",
    "LLANO V12 Laptop Cooling Pad Gaming Laptop Cooler",
    "Keyboard Protector Laptop Lenovo Ideapad Gaming 3",
]

LAPTOPS = [
    "ASUS TUF Gaming F15 RTX 3050 Laptop",
    "Lenovo Legion 5 Ryzen 7 RTX 4060",
    "Acer Nitro V15 RTX 4050",
    "HP Victus 15 Gaming Laptop",
    "MSI Thin 15 Gaming Laptop RTX 2050",
    "Lenovo LOQ 15IRX9 Gaming Laptop",
]


def test_accessories_rejected_before_budget():
    for title in ACCESSORIES:
        product = classify_product_category({"title": title, "url": ""}, "laptop gaming")

        assert product["category_decision"] == "accessory_not_laptop"
        assert product["category_score"] == 0.0


def test_real_gaming_laptops_are_kept():
    for title in LAPTOPS:
        product = classify_product_category({"title": title, "url": ""}, "laptop gaming")

        assert product["category_decision"] == "candidate_laptop"
        assert product["category_score"] > 0
