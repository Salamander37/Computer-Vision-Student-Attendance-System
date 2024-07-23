from flask import Flask, render_template, Response, send_file
import csv
from io import StringIO
from module.utils import generate_frames, load_known_faces

app = Flask(__name__)
# Initialize known faces
known_faces_dir = r"C:\Users\user\Desktop\ceevee\students"
known_faces, known_names = load_known_faces(known_faces_dir)

# List of all students (this could be dynamically loaded from a database)
all_students = set(known_names)

attendance_log = set()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/download_attendance')
def download_attendance():
    attendance_list = [{"name": student, "status": "Present" if student in attendance_log else "Absent"} for student in all_students]
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Student Name", "Status"])
    cw.writerows([(entry["name"], entry["status"]) for entry in attendance_list])
    output = si.getvalue()
    si.close()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=attendance_report.csv"})

if __name__ == "__main__":
    app.run(debug=True)