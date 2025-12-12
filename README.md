----------------------------------------------------------------------------------------
                                     Initial Setup
1. Install Dependencies
pip install flask

2. Run the API
python app.py

The server will start at: 
http://127.0.0.1:5000
----------------------------------------------------------------------------------------
                                      Commands
                 
Raw data as Admin
curl.exe -H "X-API-Key: admin-key" http://127.0.0.1:5000/raw

Summary data as Analyst
curl.exe -H "X-API-Key: analyst-key" http://127.0.0.1:5000/summary

Unauthorized test (should be denied)
curl.exe -H "X-API-Key: viewer-key" http://127.0.0.1:5000/raw
----------------------------------------------------------------------------------------
                                       Purpose
This project was created as part of a study on access control in IoT systems.
The goal was not to build a production-level security framework but to test how 
RBAC performs in a controlled environment where roles have clear boundaries.
----------------------------------------------------------------------------------------
                                        License
This project is for educational purposes only.
You may re-use or modify the code with citation.
----------------------------------------------------------------------------------------
