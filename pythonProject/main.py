from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uvicorn


class UserScore(BaseModel):
    user_email: str
    SkillName: str
    Score: int


class UserInfo(BaseModel):
    user_email: str


class UserScoreUpdate(BaseModel):
    user_email: str
    SkillName: str
    new_Score: int


key_path = "/app/skills-project-poc-6fa3b9280cec.json"
credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

client = bigquery.Client(credentials=credentials, project="skills-project-poc")

app = FastAPI()


@app.get("/employees/")
async def read_employees(email: Optional[str] = None, skill: Optional[str] = None, score: Optional[int] = None):
    query = f"SELECT * FROM `skills-project-poc.POC.user-scores-POC` WHERE 1=1"
    query_parameters = []

    if email is not None:
        query += f" AND user_email = @user_email"
        query_parameters.append(bigquery.ScalarQueryParameter("user_email", "STRING", email))
    if skill is not None:
        query += f" AND SkillName = @SkillName"
        query_parameters.append(bigquery.ScalarQueryParameter("SkillName", "STRING", skill))
    if score is not None:
        query += f" AND Score = @Score"
        query_parameters.append(bigquery.ScalarQueryParameter("Score", "INT64", score))

    job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)

    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        result_list = [dict(row) for row in results]
        if not result_list:
            raise HTTPException(status_code=404, detail="Not Found")
        return result_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insert-user-score/")
async def insert_user_score(user_score: UserScore):
    query = """
    INSERT INTO `skills-project-poc.POC.user-scores-POC` (user_email, SkillName, Score)
    VALUES (@user_email, @SkillName, @Score)
    """
    query_parameters = [
        bigquery.ScalarQueryParameter("user_email", "STRING", user_score.user_email),
        bigquery.ScalarQueryParameter("SkillName", "STRING", user_score.SkillName),
        bigquery.ScalarQueryParameter("Score", "INT64", user_score.Score)
    ]

    job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)

    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()
        return {"message": "Record inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insert-user-info/")
async def insert_user_info(user_info: UserInfo):
    timestamp = datetime.utcnow()
    query = """
    INSERT INTO `skills-project-poc.POC.user-info-POC` (timestamp, user_email)
    VALUES (@timestamp, @user_email)
    """

    query_parameters = [
        bigquery.ScalarQueryParameter("timestamp", "TIMESTAMP", timestamp),
        bigquery.ScalarQueryParameter("user_email", "STRING", user_info.user_email)
    ]

    job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)

    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()
        return {"message": "Record inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-user-info/{user_email}")
async def delete_user_info(user_email: str):
    check_query = f"""
    SELECT COUNT(*) as cnt
    FROM `skills-project-poc.POC.user-info-POC`
    WHERE user_email = @user_email
    """

    check_params = [
        bigquery.ScalarQueryParameter("user_email", "STRING", user_email)
    ]

    check_job_config = bigquery.QueryJobConfig(query_parameters=check_params)

    try:
        check_job = client.query(check_query, job_config=check_job_config)
        check_result = check_job.result()
        record_exists = next(check_result).cnt > 0

        if not record_exists:
            raise HTTPException(status_code=404, detail="Record not found")

        delete_query = f"""
        DELETE FROM `skills-project-poc.POC.user-info-POC`
        WHERE user_email = @user_email
        """

        delete_params = [
            bigquery.ScalarQueryParameter("user_email", "STRING", user_email)
        ]

        delete_job_config = bigquery.QueryJobConfig(query_parameters=delete_params)

        delete_job = client.query(delete_query, job_config=delete_job_config)
        delete_job.result()

        return {"message": "Record deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-user-score/{user_email}/{skill_name}")
async def delete_user_score(user_email: str, skill_name: str):
    # Check if the record exists
    check_query = f"""
    SELECT COUNT(*) as cnt
    FROM `skills-project-poc.POC.user-scores-POC`
    WHERE user_email = @user_email AND SkillName = @skill_name
    """
    check_params = [
        bigquery.ScalarQueryParameter("user_email", "STRING", user_email),
        bigquery.ScalarQueryParameter("skill_name", "STRING", skill_name)
    ]
    check_job_config = bigquery.QueryJobConfig(query_parameters=check_params)
    try:
        check_job = client.query(check_query, job_config=check_job_config)
        check_result = check_job.result()
        record_exists = next(check_result).cnt > 0

        if not record_exists:
            raise HTTPException(status_code=404, detail="Record not found")

        # Delete the record
        delete_query = f"""
        DELETE FROM `skills-project-poc.POC.user-scores-POC`
        WHERE user_email = @user_email AND SkillName = @skill_name
        """
        delete_params = [
            bigquery.ScalarQueryParameter("user_email", "STRING", user_email),
            bigquery.ScalarQueryParameter("skill_name", "STRING", skill_name)
        ]
        delete_job_config = bigquery.QueryJobConfig(query_parameters=delete_params)

        delete_job = client.query(delete_query, job_config=delete_job_config)
        delete_job.result()  # Wait for the query to finish

        return {"message": "User score deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/update-user-score/")
async def update_user_score(update_data: UserScoreUpdate):
    # Check if the record exists
    check_query = f"""
    SELECT COUNT(*) as cnt
    FROM `skills-project-poc.POC.user-scores-POC`
    WHERE user_email = @user_email AND SkillName = @SkillName
    """
    check_params = [
        bigquery.ScalarQueryParameter("user_email", "STRING", update_data.user_email),
        bigquery.ScalarQueryParameter("SkillName", "STRING", update_data.SkillName)
    ]
    check_job_config = bigquery.QueryJobConfig(query_parameters=check_params)
    try:
        check_job = client.query(check_query, job_config=check_job_config)
        check_result = check_job.result()
        record_exists = next(check_result).cnt > 0

        if not record_exists:
            raise HTTPException(status_code=404, detail="Record not found")

        # Update the record
        update_query = f"""
        UPDATE `skills-project-poc.POC.user-scores-POC`
        SET Score = @new_Score
        WHERE user_email = @user_email AND SkillName = @SkillName
        """
        update_params = [
            bigquery.ScalarQueryParameter("user_email", "STRING", update_data.user_email),
            bigquery.ScalarQueryParameter("SkillName", "STRING", update_data.SkillName),
            bigquery.ScalarQueryParameter("new_Score", "INT64", update_data.new_Score)
        ]
        update_job_config = bigquery.QueryJobConfig(query_parameters=update_params)

        update_job = client.query(update_query, job_config=update_job_config)
        update_job.result()  # Wait for the query to finish

        return {"message": "User score updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
