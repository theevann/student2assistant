import click
from flask_migrate import init, migrate, upgrade
from werkzeug.security import generate_password_hash

from app import app
from app.models import User, Room, Request, History, db


@click.group()
def main():
    pass


@main.command()
@click.argument('name')
@click.option('--password', '-p', default="")
@click.option('--description', '-d', default="")
def addroom(name, password, description):
    if name is "":
        print("Error: Name is empty")
        return

    if password is "":
        print("Warning: Password is empty")

    with app.app_context():
        if Room.exists(name):
            print("Error: Room {} already exists".format(name))
            return

        Room.add(name=name, password=password, description=description)
        print("Success: Room {} added".format(name))


@main.command()
@click.argument('name')
def removeroom(name):
    if name is "":
        print("Error: Name is empty")
        return

    with app.app_context():
        room = Room.get_by_name(name)
        if not room:
            print("Error: Room {} does not exist".format(name))
            return

        db.session.delete(room)
        db.session.commit()
        print("Success: Room {} deleted".format(name))


@main.command()
@click.option('--room', '-r')
def removehistories(room):
    end = "for all rooms"
    with app.app_context():
        query = History.query

        if room is not None:
            room_obj = Room.get_by_name(room)
            if room_obj is None:
                print("Error: Room {} does not exist".format(room))
                return
            query = query.filter_by(room_id=room_obj.id)
            end = "for room {}".format(room) 

        query.delete()
        db.session.commit()
        print("Success: History deleted {}".format(end))


@main.command()
def removeusers():
    with app.app_context():
        User.query.delete()
        db.session.commit()


@main.command()
def removerequests():
    with app.app_context():
        Request.query.delete()
        db.session.commit()


@main.command()
def seed():
    # os.remove('.db')
    # shutil.rmtree('migrations')
    with app.app_context():
        init()
        migrate()
        upgrade()

        Room.add(name="test", password="")



if __name__ == "__main__":
    main()
