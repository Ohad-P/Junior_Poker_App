const express = require('express');
const cors = require('cors'); // Add this line
const app = express();
const port = 3001;

app.use(cors()); // Add this line

app.get('/', (req, res) => {
  res.send('Hello, Poker!');
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
