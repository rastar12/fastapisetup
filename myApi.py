from fastapi import FastAPI,Path
from typing import Optional

app= FastAPI()

students={
    1:{"name":"John","age":20 ,"course":"Computer Science"}
}

@app.get("/")
def index():
    return{"message":"Hello world"}

# path parameter
@app.get("/students/{student_id}")
def get_student(student_id:int=Path(description="The ID of the student you want to view",gt=0,lt=3)):
    return students[student_id] 


#query parameters
@app.get("/get-by-name")
def get_student_by_name(name: Optional[str] =None, test: int=0):
    for student in students.values():
        if student["name"]==name:
            return student
    return {"message":"Student not found"}