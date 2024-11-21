import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

app=Flask(__name__)
ma=Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class meta:
        fields=("id","name","age")

class WorkoutSchema(ma.Schema):
    session_id = fields.Integer()
    member_id = fields.Integer(required=True)
    session_date=fields.Date(required=True)
    session_time=fields.String(required=True)
    activity=fields.String(required=True)

    class meta:
        fields=("session_id","member_id","session_date","session_time","activity")

member_schema=MemberSchema()
members_schema=MemberSchema(many=True)
workout_schema=WorkoutSchema()
workouts_schema=WorkoutSchema(many=True)

def connect_database():

    password="rootPassword1919"
    db="my_fitness"
    host="localhost"
    user="root"

    conn=mysql.connector.connect(
        password=password,
        database=db,
        host=host,
        user=user
    )

    return conn

@app.route("/members",methods=["POST"])
def add_member():
    try:
        member_data=member_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error":str(e)}),500

    conn=connect_database() 
    try:
        
        if not conn:
            return jsonify({"error":"could not connect to database"}),500
        cursor=conn.cursor()

        new_member=(member_data["id"],member_data["name"], member_data["age"])
        query="INSERT INTO members(id,name,age)VALUE(%s,%s,%s)"
        cursor.execute(query,(new_member))
        conn.commit()


        return jsonify({"message":"New member added"}),201

    except Error as e:
        return jsonify({"Error":str(e)})
    
    finally:
        cursor.close()
        conn.close()

@app.route("/members/<int:id>",methods=["GET"])
def get_member(id):
    try:
        member_data=member_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error":f"{e}"}),400
    
    try:
        conn=connect_database()
        cursor=conn.cursor()

        member=(member_data["id"],member_data['name'],member_data['age'])
        cursor.execute("SELECT * FROM members WHERE id = %s",(id,))
        member=cursor.fetchone()

        return jsonify(member)
    except Exception as e:
        return jsonify({"error":f"{e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
            cursor.close()

@app.route("/members",methods=["GET"])
def get_members():
    
    try:
        conn=connect_database()
        cursor=conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM members")
        members=cursor.fetchall()

        return members
    except Exception as e:
        return jsonify({"error":f"{e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
            cursor.close()

@app.route("/members/<int:id>",methods=["DELETE"])
def delete_members(id):
    try:
        member_data=member_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error":f"{e.messages}"})
    
    try:
        conn=connect_database()
        cursor=conn.cursor()

        query="DELETE FROM members WHERE id=%s"
        cursor.execute(query,(id,))
        conn.commit()

        return jsonify({"message":"member has been deleted"})
    except Exception as e:
        return jsonify({"error":f"{e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
            cursor.close()

@app.route("/members/<int:id>",methods=["PUT"])
def update_member(id):
    try:
        member_data=member_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error":f"{e.messages}"}),400
    
    try:
        member=(member_data["name"],member_data["age"])
        conn=connect_database()
        cursor=conn.cursor()
        query="UPDATE members SET name=%s,age=%s WHERE id=%s"
        cursor.execute(query,(member[0],member[1],id))
        conn.commit()
        return jsonify({"message":"Member data has been updated"})
    except Exception as e:
        return jsonify({"error":f"{e}"}),500
    finally:
        if conn and conn.is_connected():
            conn.close()
            cursor.close()


@app.route("/workout",methods=["POST"])
def workout():
    try:
        workout_data=workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error":f"{e.messages}"})
    
    try:
        conn=connect_database()
        cursor=conn.cursor()
        query="INSERT INTO workoutsessions(session_id,member_id, session_date,session_time,activity) VALUES(%s,%s,%s,%s,%s)"
        cursor.execute(query,(workout_data["session_id"],workout_data["member_id"],workout_data["session_date"],workout_data["session_time"],workout_data["activity"]))
        conn.commit()
        return jsonify({"message":"Workout Session added."}),200
    except Exception as e:
        return jsonify({"error":f"{e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
            cursor.close()

@app.route("/workout/<int:id>",methods=["PUT"])
def workout_update(id):
    try:
        workout_data=workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error":f"{e.messages}"})
    
    try:
        conn=connect_database()
        cursor=conn.cursor()
        query="UPDATE workoutsessions SET member_id=%s, session_date=%s,session_time=%s,activity=%s WHERE session_id=%s"
        cursor.execute(query,(workout_data["member_id"],workout_data["session_date"],workout_data["session_time"],workout_data["activity"],id))
        conn.commit()
        return jsonify({"message":"Workout Session changed."}),200
    except Exception as e:
        return jsonify({"error":f"{e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
            cursor.close()

@app.route("/workout",methods=["GET"])
def get_sessions():
    try:
        conn=connect_database()
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM workoutsessions")

        sessions=cursor.fetchall()
        return workouts_schema.jsonify(sessions)
    except Exception as e:
        return jsonify({"error":f"{e}"})
    finally:
        if conn and conn.is_connected():
            conn.close()
            cursor.close()

if __name__=="__main__":
    app.run(debug=True)
