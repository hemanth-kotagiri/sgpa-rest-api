<h1 align="center">RestAPI for <a href="https://github.com/hemanth-kotagiri/sgpa-calculator" target="_blank">SGPA-Calcluator</a></h1>

<p align="center">This has been specifically built to suppliment the mobile application that I am
developing. Feel free to use this irrespective of the mobile-app, with which
you can integrate into your own applications/projects to get the data. As of
now, this RestAPI provides the resluts of all R18 regulation students of the
batch 2018. Soon, I would leverage this to other regulations as well.</p>

**Note that the response is in the form of JSON only.**

### Endpoints

```
- /          - This is where you are right now.
- /result    - A query parameter specific endpoint.
- /calculate - Fetch the SGPA along with other details.
```

### Input Parameters

```
1. Hallticker Number
2. Date of Birth (YEAR-MONTH-DAY)
3. Year and Semester (YEAR,SEMESTER)
```

### Sample Response format

Below is a response object containing a 4 tuple schema.

```json
[
  {
    "subject_code": "15105",
    "subject_name": "ENGINEERING WORKSHOP",
    "grade_earned": "A+",
    "subject_credits": "2.5"
  }
]
```

And, this is a response object containing an 8 tuple schema.

```json
[
  {
    "subject_code": "15408",
    "subject_name": "DATABASE MANAGEMENT SYSTEMS LAB",
    "grade_earned": "O",
    "subject_credits": "1.5",
    "internal_marks": "25",
    "external_marks": "73",
    "total_marks": "98"
  }
]
```

Note that depending on the servers, the number of tuples are determined.

### Usage

1. You are here : https://results-restapi.herokuapp.com
2. As the above parameters have been mentioned, form the endpoint as such:

   ```
   https://results-restapi.herokuapp.com/hallticket-number/date-of-birth/year
   ```

3. Substitute your identification values in the above parameters and the RestAPI is triggered.

### Example

You could use Postman or any other service as you wish to test the RestAPI.

Copy and paste this url in a new tab:

```
  https://results-restapi.herokuapp.com/185U1A0565/2001-04-03/1,1
```

and it shall trigger the endpoint with the below response. Now, all you need to do is change the hallticket-number and the date-of-brith to trigger the endpoint to fetch the specific results.

You would obtain the response object as follows along with the detals of the student such as Hallticket number, Name, Father's Name and the College Code:

```json
[
  {
    "HTNO": "Hallticket Number",
    "NAME": "Student Name",
    "FATHER NAME": "Student's Father Name",
    "COLLEGE CODE": "Code"
  },
  [
    {
      "subject_code": "15105",
      "subject_name": "ENGINEERING WORKSHOP",
      "grade_earned": "A+",
      "subject_credits": "2.5"
    },
    {
      "subject_code": "15106",
      "subject_name": "ENGINEERING CHEMISTRY LAB",
      "grade_earned": "A+",
      "subject_credits": "1.5"
    },
    {
      "subject_code": "15107",
      "subject_name": "ENGLISH LANGUAGE AND COMMUNICATION SKILLS LAB",
      "grade_earned": "O",
      "subject_credits": "1"
    },
    {
      "subject_code": "15108",
      "subject_name": "BASIC ELECTRICAL ENGINEERING LAB",
      "grade_earned": "O",
      "subject_credits": "1"
    },
    {
      "subject_code": "151AA",
      "subject_name": "MATHEMATICS  I",
      "grade_earned": "B+",
      "subject_credits": "4"
    },
    {
      "subject_code": "151AF",
      "subject_name": "CHEMISTRY",
      "grade_earned": "C",
      "subject_credits": "4"
    },
    {
      "subject_code": "151AG",
      "subject_name": "BASIC ELECTRICAL ENGINEERING",
      "grade_earned": "A",
      "subject_credits": "3"
    },
    {
      "subject_code": "151AH",
      "subject_name": "ENGLISH",
      "grade_earned": "A",
      "subject_credits": "2"
    }
  ]
]
```

In the case of the calculate endpoint, form the url as such:

```
https://results-restapi.herokuapp.com/calculate/hallticket-number/date-of-birth/year
```

This will add an additional object as such:

```json
{
  "SGPA": "Value"
}
```

[MIT License](https://github.com/hemanth-kotagiri/sgpa-rest-api/blob/master/LICENSE) - Copyright (c) 2021 Hemanth Kotagiri

Made with ❤️ by Hemanth
