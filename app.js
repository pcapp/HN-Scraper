const { MongoClient } = require("mongodb");
const sgMail = require("@sendgrid/mail");
const seedrandom = require("seedrandom");

require("dotenv").config();

sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const url = process.env.DB_URL;
const dbName = process.env.DB_NAME;

const client = new MongoClient(url);
const rng = seedrandom(process.env.RANDOM_SEED);

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

function sleep() {
  const time = Math.round(500 + rng() * 250);
  return new Promise((resolve) => setTimeout(resolve, time));
}

async function sendEmail(subject, message) {
  const msg = {
    to: "peter.cappetto@gmail.com",
    from: "peter@petercappetto.com",
    subject,
    text: message,
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

    for (let itemId = startId; itemId < endId; ++itemId) {
      console.log(`Process item ${itemId}`);
      const data = await getItem(itemId);

      const db = client.db(dbName);
      const items = db.collection("items");
      const filter = { id: data.id };
      const update = {
        $set: data,
      };

      await items.updateOne(filter, update, { upsert: true });
      await sleep();
    }

    await sendEmail("Worker done", "Finished processing all the items");
  } catch (err) {
    console.error(err);
    await sendEmail(
      "Worker error",
      `
    An error occurred: ${err}
    `
    );
  } finally {
    await client.close();
  }
}

main().catch(console.error);
