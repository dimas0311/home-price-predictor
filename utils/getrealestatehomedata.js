export async function getRealEstateHomeData() {
  try {
    const response = await fetch("/api/realestate");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching realestate home data:", error);
    return [];
  }
}
