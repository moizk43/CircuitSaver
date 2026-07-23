# """
# watttime_register.py
# Run this ONCE to create your WattTime account.
# """

# import os
# from dotenv import load_dotenv
# from watttime import WattTimeMyAccess

# load_dotenv()

# WATTTIME_USERNAME = os.getenv("WATTTIME_USERNAME")
# WATTTIME_PASSWORD = os.getenv("WATTTIME_PASSWORD")

# wt = WattTimeMyAccess(username=WATTTIME_USERNAME, password=WATTTIME_PASSWORD)

# try:
#     wt.register(email="moizkothawala@gmail.com", organization="CircuitSaver")
#     print("Registration submitted successfully.")
# except Exception as e:
#     print("Registration failed with error:")
#     print(e)
#     if hasattr(e, "response") and e.response is not None:
#         print("Response body:", e.response.text)