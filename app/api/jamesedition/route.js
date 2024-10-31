import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export async function GET() {
  try {
    const filePath = path.join(
      process.cwd(),
      "script",
      "jamesedition_home_data.json"
    );
    const jsonData = await fs.readFile(filePath, "utf8");
    const homeData = JSON.parse(jsonData);

    const getHomeIdFromUrl = (url) => {
      const idRegex = /\/home\/(\d+)$/;
      const match = url.match(idRegex);
      return match ? match[1] : null;
    };

    const getCityFromAddress = (address) => {
      const parts = address.split(",");
      if (parts.length >= 2) {
        return parts[parts.length - 2].trim();
      }
      return null;
    };

    const roundArea = (area) => {
      return Math.round(parseFloat(area));
    };
    const roundUsd = (price) => {
      return Math.round(parseFloat(price));
    };
    // Create a Map to store unique homes by URL
    const uniqueHomes = new Map();

    let counter = 1;

    const formattedHomeData = homeData.forEach((home) => {
      if (!uniqueHomes.has(home?.home_url)) {
        // Extract the last part of URL (e.g., "house-alderney-14853119")
        const urlPart = home?.home_url.split("/").pop();
        // Create unique key with JamesEidtion and listing details
        const uniqueKey = `JamesEdition_${urlPart}`;

        uniqueHomes.set(home.home_url, {
          key: uniqueKey,
          id: uniqueKey,
          home_url: home?.home_url,
          image_link: home?.image_link,
          address: home?.address,
          city: home?.address_locality,
          country: home?.address_country,
          latitude: home?.latitude,
          longitude: home?.longitude,
          price: home?.price_usd.split(".")[0],
          beds: home?.beds,
          baths: home?.baths,
          area: home?.area_sqft.split(".")[0],
          source: "JamesEidtion",
        });
      }
    });

    // Convert Map values to array
    const uniqueHomeArray = Array.from(uniqueHomes.values());

    return NextResponse.json(uniqueHomeArray);
  } catch (error) {
    console.error("Error reading or parsing home data:", error);
    return NextResponse.json(
      { error: "Failed to fetch home data" },
      { status: 500 }
    );
  }
}
