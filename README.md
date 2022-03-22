# blockchain python
A simple API implementation of blockchain proof of work cryptocurrency using python. The application supports the running of multiple instances (Nodes) that communicate and synchronize. Implemented features are:

- create wallet
- load wallet
- create transaction
- mine blocks
- view balance
- view open (unmined) transactions
- add peer nodes
- view peer nodes

## Setup

Clone repository and change directory into the repository directory.
Make sure python3 is installed, then, use the auto scrip or the manual method below to start the application

##### Auto script (Mac or Linux)

run the bash script to set up and start application:
`./run.sh`

##### Manual

create a virtual environment (run the two commands below
`python3 -m venv venv`
`source ./venv/bin/activate`

install requirements
`pip install -r requirements.txt`

start app
`python ./run.py`

## Usage

Example of supported endpoints

### wallet

**POST Request**

> Description: Creates and returns new keys (private and public)

> Method: `POST`

> Content-type: `application/json`

> Request body format: {} / None

> Path: `/wallet`

**GET Request**

> Description: Returns previous keys

> Method: `GET`

> Path: `/wallet`

**Response**:

> Type: `JSON`

> Format: `{funds: 0, private_key: "some key", public_key: "some key"}`

**Status codes**

> 200: keys retrieved and returned

> 201: keys created and returned

> 500: error with server

---

### Balance

**GET Request**

> Description: Retrieves node balance

> Method: `GET`

> Path: `/balance`

**response**

> Type: `JSON`

> Format: `{funds: 0, message: "Fetched balance successfully"}`

**Status codes**

> 200: ok

> 500: Server error

---

### Open transactions

**GET Request**

> Description: Retrieves open transactions

> Method: `GET`

> Path: `/transactions`

**response**

> Type: `JSON`

> Format: `[Transaction,]`

**Status codes**

> 200: ok

---

### Mine block

**Request**

> Description: Mine block for a fee

> Method: `POST`

> Path: `/mine`

**response**

> Type: `JSON`

> Format: `{funds: 0, message: "", block: <Block>}`

**Status codes**

> 201: block mined successfully

> 409: chain has conflicts that need resolving

> 500: Server error

---

### Resolve conflicts

**Request**

> Description: Resolve conflicts with local chain

> Method: `POST`

> Path: `/resolve-conflicts`

**response**

> Type: `JSON`

> Format: `{message: ""}`

**Status codes**

> 200: ok

---

### Read chain

**GET Request**

> Description: Returns the chain of blocks

> Method: `GET`

> Path: `/chain`

**response**

> Type: `JSON`

> Format: `[<Block>,]`

**Status codes**

> 200: ok

---

### Peer nodes

**POST Request**

> Description: add a node (url) to peer list

> Method: `POST`

> Path: `/nodes`

> Content-type: `application/json`

> Request body format: `{"node": "localhost:3001"}`

**GET Request**

> Description: rerurns a list of peer nodes

> Method: `GET`

> Path: `/nodes`

**DELETE Request**

> Description: deletes a node

> Path: `/nodes/<node>`

**response**

> Type: `JSON`

> Format: `{message: "", nodes: [...]}`

**Status codes**

> 200: ok

> 201: added

> 400: client error

---

### Add transaction

**Request**

> Description: adds a transaction

> Method: `POST`

> Path: `/transaction`

> Content-type: `application/json`

> Request body format: `{"recipient": "public_key", amount: <number>}`

**response**

> Type: `JSON`

> Format: `{message: "", funds:<number>, transaction: <Transaction>}`

**Status codes**

> 201: added

> 400: client error

> 500: server error

---

### Objects

Transaction

```json
{
  "amount": 2,
  "recipient": "",
  "sender": "",
  "signature": ""
}
```

Block

```json
{
  "funds": "",
  "message": "URL found",
  "transaction": <Transaction>
}
```
