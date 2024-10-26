export async function getRedfinHomeData() {
  try {
    const response = await fetch("/api/redfin");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching redfin home data:", error);
    return [];
  }
}
