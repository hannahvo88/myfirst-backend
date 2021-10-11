import mariadb
from flask import Flask, request, Response
import dbcreds
import json
import sys

app = Flask(__name__)

@app.route('/api/blog', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def post_handler():
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        if request.method == 'GET':
            cursor.execute("SELECT * from posts")
            contents = cursor.fetchall()
            print(contents)
            return Response(json.dumps(contents), 
                            mimetype="application/json", 
                            status=200)
            
        elif request.method == 'POST':
            data = request.json.get('post')

            if len(data) == 1:
                content = data.get("content")
                cursor.execute("INSERT INTO posts(content) VALUES(?)", [content])
                conn.commit()
                
                cursor.execute("SELECT * FROM posts WHERE content=?", [content])
                new_content = cursor.fetchone()

                resp = {
                    "id": new_content,
                    "content": new_content
                }

                return Response(json.dumps(resp),
                                "You have a new post",
                                mimetype="application/json", 
                                status=201)
            else:
                
                return Response("Error! Something went wrong", 
                                mimetype="text/plain", 
                                status=400)

        elif request.method == 'PATCH':
            data = request.json

            if len(data) == 2:
                tweet_id = data.get("id")
                content_updated = data.get("content")

                cursor.execute("SELECT EXISTS(SELECT * FROM posts WHERE id=?)", [tweet_id])
                user = cursor.fetchone()
                if user == 1:
                    cursor.execute("UPDATE posts SET content=? WHERE id=?", [content_updated, tweet_id])
                    conn.commit()
                    return Response("Your post has updated", 
                                    mimetype="text/plain", 
                                    status=200)
                else:
                    
                    return Response("Your post has NOT been posted", 
                                    mimetype="text/plain", 
                                    status=400)
            
            elif request.method == 'DELETE':
                data = request.json

            if len(data) == 1:
                tweet_id = data.get("id")
                cursor.execute("SELECT EXISTS(SELECT * FROM posts WHERE id=?)", [ tweet_id])
                old_post = cursor.fetchone()[0]
                if old_post == 1:
                    cursor.execute("DELETE FROM posts WHERE id=?", [ tweet_id])
                    conn.commit()
                    return Response("Your post has been deleted", 
                                    mimetype="text/plain", 
                                    status=200)
                else:
                    print("Sorry! Something went wrong")
                    return Response("Sorry! Something went wrong", 
                                    mimetype="text/plain", 
                                    status=400)
            else:
                print("Invalid")
                return Response("Invalid", 
                                mimetype="text/plain", 
                                status=200)

        else:
            print("Something went wrong! Please check again.")

    except mariadb.OperationalError:
        print("There seems to be a connection issue!")
    except mariadb.ProgrammingError:
        print("Apparently you do not know how to code")
    except mariadb.IntergrityError:
        print("Error with DB integrity, most likely consraint failure")
    except:
        print("Opps! Somthing went wrong")
    finally:
        if (cursor != None):
            cursor.close()
        else:
            print("No cursor to begin with.")
        
        if (conn != None):
            conn.rollback()
            conn.close()
        else:
            print("No connection!")


if len(sys.argv) > 1:
    mode = sys.argv[1]
    if mode == "production":
        import bjoern
        host = "0.0.0.0"
        port = 5000
        print("Server is running in production mode")
        bjoern.run(app, host, port)
    elif mode == "testing":
        from flask_cors import CORS
        CORS(app)
        print("Server is running in testing mode, switch to production when needed")
        app.run(debug=True)
    else:
        print("Invalid mode argement, exiting")
        exit()
    
else:
    print("No arrgements")
    exit()