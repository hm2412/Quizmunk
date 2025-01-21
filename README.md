# Team Chipmunk Large Group project

## Team members
The members of the team are:
- Tameem Al-Tamimi
- Kyran Bailey
- Khadija Hashim
- Isa Hussain
- Muhammed (Areeb) Iqbal
- Adam Jacobs
- Haleema Mohammed
- Hassan Muddassir
- Abdullah Muzahir
- Ahmet Taramis

## Project structure

## Deployed version of the application
The deployed version of the application can be found ...

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*Note: if css styling is not visible, clear cache*

## Sources
The packages used by this application are specified in `requirements.txt`