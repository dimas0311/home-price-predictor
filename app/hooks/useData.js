"use client";
import React, {
  createContext,
  useState,
  useContext,
  useEffect,
  useCallback,
} from "react";
import { getRedfinHomeData } from "../../utils/getredfinhomedata";
import { getJamesEditionHomeData } from "../../utils/getjameseditionhomedata";
import { getStateData } from "../../utils/getstatedata";

const DataContext = createContext();

const HOME_STORE = "homeData";
const ALL_STORE = "allData";
const STATE_STORE = "stateData";
const TIMESTAMP_KEY = "dataTimestamp";

export const HomeDataProvider = ({ children }) => {
  const [homeData, setHomeData] = useState([]);
  const [stateData, setStateData] = useState([]);
  const [allData, setAllData] = useState([]);
  const [loading, setLoading] = useState(true);

  const saveToStorage = (key, data) => {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
      console.error(`Error saving data to localStorage: ${error}`);
    }
  };

  const getFromStorage = (key) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error(`Error retrieving data from localStorage: ${error}`);
      return null;
    }
  };

  const getAllData = useCallback(async () => {
    setLoading(true);
    try {
      const cachedAllData = getFromStorage(ALL_STORE);
      const cachedHomeData = getFromStorage(HOME_STORE);
      const cachedStateData = getFromStorage(STATE_STORE);
      const cachedTimestamp = getFromStorage(TIMESTAMP_KEY);

      if (
        cachedAllData &&
        cachedHomeData &&
        cachedStateData &&
        cachedTimestamp &&
        Date.now() - cachedTimestamp < 3600000 // 1 hour
      ) {
        setHomeData(cachedHomeData);
        setStateData(cachedStateData);
        setAllData(cachedAllData);
        setLoading(false);
        return;
      }

      const preJamesEditionHomeData = await getJamesEditionHomeData();
      const jamesEditionHomeData = preJamesEditionHomeData.filter(
        (home) => home.image_link !== "N/A"
      );

      console.log("preJamesEditionHomeData", preJamesEditionHomeData?.length);

      const preRedfinHomeData = await getRedfinHomeData();
      const redfinHomeData = preRedfinHomeData.filter(
        (home) =>
          home.image_link !==
          "https://ssl.cdn-redfin.com/photo/92/islphoto/870/genIslnoResize.3231870_0.jpg"
      );

      const stateData = await getStateData();

      function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
      }

      const combinedData = shuffleArray([
        ...redfinHomeData,
        ...jamesEditionHomeData,
      ]);

      const allHomeData = [...preRedfinHomeData, ...preJamesEditionHomeData];

      console.log("allHomeData", allHomeData?.length);

      saveToStorage(ALL_STORE, allHomeData);
      saveToStorage(HOME_STORE, combinedData);
      saveToStorage(STATE_STORE, stateData);
      saveToStorage(TIMESTAMP_KEY, Date.now());

      setAllData(allHomeData);
      setHomeData(combinedData);
      setStateData(stateData);
    } catch (error) {
      console.error("Error fetching or caching data:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    getAllData();
  }, [getAllData]);

  return (
    <DataContext.Provider
      value={{
        allData,
        homeData,
        stateData,
        loading,
        refreshEvents: getAllData,
      }}>
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error("useData must be used within an DataProvider");
  }
  return context;
};
