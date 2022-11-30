import os, dotenv
dotenv.load_dotenv(verbose=True)

email = os.getenv('EMAIL_PASS')
print(email)