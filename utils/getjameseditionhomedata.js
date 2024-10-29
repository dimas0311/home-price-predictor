export async function getJamesEditionHomeData() {
  try {
    const response = await fetch("/api/jamesedition");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching jamesedition home data:", error);
    return [];
  }
}
