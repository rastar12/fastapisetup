from fastapi import FastAPI,Path # for path parameters
from typing import Optional # for optional query parameters
from pydantic import BaseModel # for request body

app= FastAPI()

students={
    1:{"name":"John","age":20 ,"course":"Computer Science"}
}

class Student(BaseModel):
    name: str
    age: int
    course: str

class UpdateStudent(BaseModel):
    name:Optional[str]=None
    age: Optional[int]=None


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


# combining path and query parameters

@app.get("/get-by-id/{student_id}")
def get_student_by_id(student_id:int, test: int=0):  # test is a query parameter, student_id is a path parameter
    if student_id in students:
        return students[student_id]
    return {"message":"Student not found"}

# request body and the post method 

@app.post("/create-student/{student_id}")
def create_student(student_id: int, student: Student):
    if student_id in students:
        return {"message":"Student already exists"}
    students[student_id]=student.dict() # convert the student object to a dictionary
    return students[student_id]


#put method for updatting a student

@app.put("/update-student/{student_id}")
def update_student(student_id:int, student: UpdateStudent):
    if student_id not in students:
        return {"message":"Student does not exist"}
    students[student_id].update(student.dict(exclude_unset=True)) # update the student with the new data, exclude_unset=True will only update the fields that are provided in the request body 
    return students[student_id]