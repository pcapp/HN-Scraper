const { MongoClient } = require("mongodb");
const sgMail = require("@sendgrid/mail");

require("dotenv").config();

sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const url = process.env.DB_URL;
const dbName = process.env.DB_NAME;

const client = new MongoClient(url);

async function getItem(itemNumber) {
  const url = `https://hacker-news.firebaseio.com/v0/item/${itemNumber}.json`;

  let numTries = 1;
  let maxTries = 3;

  while (numTries < maxTries) {
    try {
      const response = await fetch(url);
      const data = await response.json();

      return data;
    } catch (error) {
      numTries++;
    }
  }

  if (numTries == maxTries) {
    throw new Error(
      `Tried to get item ${itemNumber} ${maxTries} times and failed.`
    );
  }
}

async function sendDoneEmail() {
  const msg = {
    to: "peter.cappetto@gmail.com",
    from: "peter@petercappetto.com", // Change to your verified sender
    subject: "Worker completed",
    text: "and easy to do anywhere, even with Node.js",
    html: "<strong>and easy to do anywhere, even with Node.js</strong>",
  };

  await sgMail.send(msg);
}

async function main() {
  try {
    if (process.argv.length != 5) {
      console.error("Usage: scraper <worker_id> <start_id> <end_id>");
      process.exit(1);
    }

    const workerId = parseInt(process.argv[2]);
    const startId = parseInt(process.argv[3]);
    const endId = parseInt(process.argv[4]);
    console.log(`Worker ${workerId} fetching ${startId} to ${endId}`);

    await client.connect();

    // const startId = 39422168;
    // const endId = startId + 10;

    for (let itemId = startId; itemId < endId; ++itemId) {
      const data = await getItem(itemId);

      const db = client.db(dbName);
      const items = db.collection("items");
      const filter = { id: data.id };
      const update = {
        $set: data,
      };

      await items.updateOne(filter, update, { upsert: true });
    }

    // await sendDoneEmail();
  } catch (err) {
    console.error(err);
  } finally {
    await client.close();
  }
}

main().catch(console.error);
