import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export async function GET() {
  try {
    const filePath = path.join(
      process.cwd(),
      "script",
      "real_estate_data.json"
    );
    const jsonData = await fs.readFile(filePath, "utf8");
    const homeData = JSON.parse(jsonData);

    const roundArea = (area) => {
      return Math.round(parseFloat(area)); // 2. Need Math.round and parseFloat
    };

    // Create a Map to store unique homes by URL
    const uniqueHomes = new Map();

    const formattedHomeData = homeData["listings"].forEach((home) => {
      // Only keep the first occurrence of each home_url
      if (!uniqueHomes.has(home.home_url)) {
        uniqueHomes.set(home.home_url, {
          key: home?.key,
          id: home?.id,
          home_url: home?.home_url,
          image_link: home?.image_link,
          address: home?.address,
          city: home?.city,
          country: home?.country,
          latitude: home?.latitude,
          longitude: home?.longitude,
          price: `$${roundArea(home?.price_usd)}`,
          beds: `${home?.beds} beds`,
          baths: `${home?.baths} baths`,
          area: roundArea(home?.area_sqft),
          source: "RealEstate",
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
