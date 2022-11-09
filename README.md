<h1 align="center"><a href="http://results.jntuh.ac.in/" target="_blank">JNTUH</a> Engineering Results REST-API</h1>

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/9ca1efa8af8a450abe751428a6fbbbf1)](https://app.codacy.com/gh/hemanth-kotagiri/sgpa-rest-api?utm_source=github.com&utm_medium=referral&utm_content=hemanth-kotagiri/sgpa-rest-api&utm_campaign=Badge_Grade_Settings)
![License](https://img.shields.io/github/license/hemanth-kotagiri/sgpa-rest-api)
![Stars](https://img.shields.io/github/stars/hemanth-kotagiri/sgpa-rest-api)

<div align="left">
  <img width=100 src="https://img.shields.io/badge/flask-black.svg?style=for-the-badge&logo=flask" alt="">
  <img width=110 src="https://img.shields.io/badge/python-black.svg?style=for-the-badge&logo=python" alt="">
  <img width=120 src="https://img.shields.io/badge/selenium-black.svg?style=for-the-badge&logo=selenium" alt="">
  <img width=100 src="https://img.shields.io/badge/redis-black.svg?style=for-the-badge&logo=redis" alt="">
</div>

This has been specifically built to suppliment the <a href="https://github.com/hemanth-kotagiri/sgpa-calculator" target="_blank">mobile application</a> that I have
developed. Feel free to use this irrespective of the mobile-app, with which
you can integrate into your own applications/projects to get the data. This
RestAPI provides the results for all regulations, and of all types (
regular and supplementary ).

### Documentation

An official documentation website for the API is available at [SGPA RestAPI
Docs](https://hemanth-kotagiri.github.io/sgpa-rest-api-docs/). Please check it
out for more information.

**Note that the response is in the form of JSON only**

### Endpoints

```
- /                   - This is where you are right now.
- /result             - A query parameter specific endpoint.
- /calculate          - Fetch the SGPA along with other details.
- /new/all            - Fetch all results links (Supplementary and Regular).
- /new/all/regular    - Fetch all regular results links.
- /new/all/supply     - Fetch all regular supplementary links.
- /api                - A Query parameter endpoint to get result of an exam given hallticket, date of birth, degree, examCode, eType, type and result.
- /api/calculate      - A Query parameter endpoint to get result of an exam given hallticket, date of birth, degree, examCode, eType, type and result with sgpa.
- /api/bulk/calculate - A Query parameter endpoint to get results of multiple halltickets given other parameters such as degree, examCode, eType, type, result and grade along with SGPA.
- /new/               - Returns all results links in unordered fashion
- /notifications      - Returns all the latest released notifications
```

Refer to the official documentation for detailed API Reference. Below is
just a sample from one endpoint. Please click
[here](https://hemanth-kotagiri.github.io/sgpa-rest-api-docs/).

### API Reference

The below example is to fetch results for R-18 (2018) Regular Exams only. To
get other results, please refer to the [API
Documentation](https://hemanth-kotagiri.github.io/sgpa-rest-api-docs/).

#### Get results and student details

```http
  GET /hallticket/dob/year
```

#### Query parameter specific endpoint

```http
  GET /result?hallticket&dob&year
```

#### Endpoint to calculate the sgpa

```http
  GET /calculate/hallticket/dob/year
```

| Parameter    | Type     | Description                                        |
| :----------- | :------- | :------------------------------------------------- |
| `Hallticket` | `string` | **Required**: Your Hallticket Number               |
| `dob`        | `string` | **Required**: Your Date of Birth (YYYY-MM-DD)      |
| `Year`       | `string` | **Required**: Desired Year and Semester (year,sem) |

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

##### Note that depending on the servers, the number of tuples are determined

### Usage

1. You are here : https://results-restapi.herokuapp.com

2. As the above parameters have been mentioned, form the endpoint as such:

   ```
   https://results-restapi.herokuapp.com/hallticket-number/date-of-birth/year
   ```

3. Substitute your identification values in the above parameters and the
   RestAPI is triggered.

### Example

You could use Postman or any other service as you wish to test the RestAPI.

Copy and paste this url in a new tab:

```
  https://results-restapi.herokuapp.com/185U1A0565/2001-04-03/1,1
```

and it shall trigger the endpoint with the below response. Now, all you need to
do is change the hallticket-number and the date-of-brith to trigger the
endpoint to fetch the specific results.

You would obtain the response object as follows:

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

[GNU GPLv3](LICENSE) - Copyright (c) 2021 Hemanth Kotagiri

This project has been solely developed by me without any external influence by
a person or an organization or university whatsoever, and if in the case of any
upcoming contributions, they are also equally regarded as developers of this
project.

Contributions are always welcome! Feel free to pick up tasks from the project
section and raise a PR.
Please raise an issue regarding the task that you would like to pick up and
link the PRs for the same.

Made with ❤️ by Hemanth.

> I started this for you, only for you. Now, it serves for a greater purpose -
> for so many students ahead. You shall be remembered forever, in the
> reminiscence of this project.

> **_For Precious, with Patience._**
