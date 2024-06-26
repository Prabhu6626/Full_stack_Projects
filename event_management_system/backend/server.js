const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

mongoose.connect('mongodb://localhost:27017/event-management', { useNewUrlParser: true, useUnifiedTopology: true });

const userSchema = new mongoose.Schema({
  email: String,
  password: String,
});

const User = mongoose.model('User', userSchema);

app.post('/api/register', async (req, res) => {
  const { email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);
  const user = new User({ email, password: hashedPassword });
  await user.save();
  res.sendStatus(201);
});

app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user) return res.status(400).send('Invalid email or password');

  const isValid = await bcrypt.compare(password, user.password);
  if (!isValid) return res.status(400).send('Invalid email or password');

  const token = jwt.sign({ _id: user._id }, 'secretKey');
  res.json({ token });
});

app.listen(5000, () => {
  console.log('Server running on http://localhost:5000');
});
