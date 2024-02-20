from ultralytics import YOLO
import cv2
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
import time, math

# Define the database model
Base = declarative_base()
class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    class_label = Column(String)
    check_in = Column(Integer)
    check_out = Column(Integer)
    total_time_spent = Column(Integer)  # Added 'total_time_spent' column
    day_of_week = Column(String)

# Starting measuring time and day
timer = time.time()
day = 1  

# class labels
class_names = ["maryam", "shaheen"]

# Load the YOLO model
model = YOLO('./best.pt') #Change path according to your best.pt filepath

# Connect to SQLite database
engine = create_engine('sqlite:///attendance.db')  # Change the database URL as needed
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

cap = cv2.VideoCapture(0)
counter=0
entered_frame = False
attendees = {}  # Dictionary to store check-in times

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    if round(time.time() - timer) > 24:
        timer = time.time()
        day = (day%7)+1
    
    # Perform object detection on the frame
    results = model(frame)    
    boxes = results[0].boxes
    if not boxes:
        if entered_frame and counter > 5: 
            # This person is recognized for the first time, mark as check-in
            attendees[class_label] = {'check_in': math.floor(checkin)}
            print("Check in Time Noted!")
        counter=0
        entered_frame = False
   
    # Process YOLOv8 detection results
    for pred in boxes:
        label = int(pred.cls)
        confidence = float(pred.conf)
        if label==int(pred.cls):
            entered_frame = True
            counter=counter+1
        print(counter)
    
        
        # Check if the confidence is above a certain threshold (e.g., 0.5)
        if confidence > 0.5:
            x, y, w, h = map(int, pred.xyxy[0])

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)

            # Add class label text
            class_label = class_names[label]
            cv2.putText(frame, f'{class_label}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Check if the person is already in the attendees dictionary
            if class_label in attendees and attendees[class_label]['check_in']:
                # This person is recognized again, mark as check-out
                attendees[class_label]['check_out'] = math.floor(time.time() - timer)
                check_out = attendees[class_label]['check_out']

                print("Check out time noted")

                # Calculate total time spent in seconds
                total_time_spent = math.floor(check_out - attendees[class_label]['check_in'])
                if total_time_spent < 0:
                    total_time_spent = math.floor(24 - abs(total_time_spent))

                # Save check-out time and total time spent to the database
                attendance = Attendance(class_label=class_label,
                                        check_in=attendees[class_label]['check_in'],
                                        check_out=check_out,
                                        total_time_spent=total_time_spent,
                                        day_of_week=f"day {day}")
                session.add(attendance)
                session.commit()
                del attendees[class_label]  # Remove the person from the dictionary
                
            else:
                if counter>20:
                    cv2.putText(frame, 'Move from the front', ((x+w)//2, (y+h)//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                checkin = time.time() - timer 
                print(f"{round(checkin)}hours")

    cv2.imshow('Video', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
