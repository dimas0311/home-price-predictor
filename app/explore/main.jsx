"use client";
import React, { useState, useEffect, useMemo } from "react";
import { Card } from "@/app/components/card";
import { LoadingComponent } from "@/app/components/loading";
import Image from "next/image";
import Link from "next/link";
import { useData } from "../hooks/useData";
import { AutoComplete, Input, Button, DatePicker, Slider } from "antd";
import PriceRangeSlider from "@/app/components/slider";
import MapView from "@/app/components/map";
import ScrollToTopButton from "@/app/components/totop";
import axios from "axios";
import moment from "moment";

const { RangePicker } = DatePicker;

export const MainPage = () => {
  const redfinLink = "www.redfin/com";
  const { homeData, stateData, loading, allData } = useData();

  const [filteredData, setFilteredData] = useState(homeData);
  const [bedsSearchTerm, setBedsSearchTerm] = useState("");
  const [bathsSearchTerm, setBathsSearchTerm] = useState("");
  const [citySearchTerm, setCitySearchTerm] = useState("");
  const [dateRange, setDateRange] = useState(null);
  const [priceRange, setPriceRange] = useState([0, 10000000]);
  const [options, setOptions] = useState([]);
  const [bOptions, setBOptions] = useState([]);
  const [displayCount, setDisplayCount] = useState(60);

  const [selectedCityData, setSelectedCityData] = useState(null);

  useEffect(() => {
    setFilteredData(homeData);
  }, [homeData]);
  console.log("hn", homeData?.length);
  console.log("all_data", allData?.length);
  // console.log("sn", stateData?.length);
  // console.log("sn", stateData?.slice(0, 3));
  // console.log("hn", homeData?.slice(0, 3));

  const cityOptions = Array.from(
    new Set(
      homeData
        .map((home) => home?.city)
        .filter((city) => city && city.trim() !== "" && !/\d/.test(city)) // Added number check
    )
  )
    .map((city) => ({ value: city, label: city }))
    .sort((a, b) => a.label.localeCompare(b.label));

  const handleSearch = () => {
    const filtered = homeData.filter((home) => {
      const price = parseFloat(home?.price?.replace(/[^0-9.-]+/g, ""));
      return (
        (bedsSearchTerm === "" ||
          home?.beds?.toLowerCase() === bedsSearchTerm.toLowerCase()) &&
        (bathsSearchTerm === "" ||
          home?.baths?.toLowerCase() === bathsSearchTerm.toLowerCase()) &&
        (citySearchTerm === "" ||
          home?.city?.toLowerCase() === citySearchTerm.toLowerCase()) &&
        price >= priceRange[0] &&
        price <= priceRange[1]
      );
    });
    setFilteredData(filtered);
    setDisplayCount(60);

    if (citySearchTerm) {
      const cityData = stateData.find((data) => data.city === citySearchTerm);
      setSelectedCityData(cityData);
    } else {
      setSelectedCityData(null);
    }
  };
  // console.log("=============citySearchTerm===============", citySearchTerm);
  // console.log("===========selectedCityData==============", selectedCityData);

  const handleClearSearch = () => {
    setBedsSearchTerm("");
    setBathsSearchTerm("");
    setCitySearchTerm("");
    setFilteredData(homeData);
    setDateRange(null);
    setOptions([]); // Reset options for AutoComplete
    setBOptions([]);
    setDisplayCount(60);
    setPriceRange([0, 10000000]);
    setSelectedCityData(null);
  };

  const bedsOptions = useMemo(() => {
    return Array.from(new Set(homeData.map((home) => home?.beds)))
      .filter((beds) => beds !== "1 beds")
      .sort((a, b) => {
        // Handle null/undefined/dash cases
        if (a === null || a === undefined || a === "—") return 1;
        if (b === null || b === undefined || b === "—") return -1;
        // Sort numerically
        return parseFloat(a) - parseFloat(b);
      })
      .map((beds) => ({
        value: beds,
        label:
          beds === "—" ||
            beds === null ||
            beds === undefined ||
            beds === "0 beds"
            ? "— beds"
            : `${beds}`,
      }));
  }, [homeData]);

  const bathsOptions = useMemo(() => {
    return Array.from(new Set(homeData.map((home) => home?.baths)))
      .sort((a, b) => {
        // Handle null/undefined/dash cases
        if (a === null || a === undefined || a === "—") return 1;
        if (b === null || b === undefined || b === "—") return -1;
        // Sort numerically
        return parseFloat(a) - parseFloat(b);
      })
      .map((baths) => ({
        value: baths,
        label:
          baths === "—" || baths === null || baths === undefined
            ? "— baths"
            : `${baths}`,
      }));
  }, [homeData]);

  const onBedsSearch = (searchText) => {
    setBedsSearchTerm(searchText);
    if (searchText === "") {
      setOptions(bedsOptions); // Show all options when search text is empty
    } else {
      const filteredOptions = bedsOptions.filter((option) =>
        option.value.toLowerCase().includes(searchText.toLowerCase())
      );
      setOptions(filteredOptions);
    }
  };

  const onBathsSearch = (searchText) => {
    setBathsSearchTerm(searchText);
    if (searchText === "") {
      setBOptions(bathsOptions); // Show all options when search text is empty
    } else {
      const filteredOptions = bathsOptions.filter((option) =>
        option.value.toLowerCase().includes(searchText.toLowerCase())
      );
      setBOptions(filteredOptions);
    }
  };

  const inputStyle = {
    fontFamily: "Helvetica",
    height: "45px",
    fontSize: "26px",
  };

  const autoCompleteStyle = {
    fontSize: "26px", // Base font size for the component
  };

  const dropdownStyle = {
    fontSize: "26px", // Font size for dropdown items
  };

  return (
    <div className="min-h-screen bg-black font-helvetica">
      {!loading ? (
        <div className="px-6 pt-[80px] mx-auto max-w-[160rem] lg:px-8">
          <div className="flex flex-col items-center w-full space-y-3 p-2 rounded-lg shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 w-full max-w-8xl">
              <AutoComplete
                className="w-full"
                style={{ fontSize: "28px" }} // Add this for dropdown menu styling
                options={options}
                onSearch={onBedsSearch}
                onSelect={(value) => setBedsSearchTerm(value)}
                onChange={(value) => setBedsSearchTerm(value)}
                value={bedsSearchTerm}
              >
                <Input
                  size="large"
                  placeholder="Search by beds"
                  style={inputStyle}
                />
              </AutoComplete>
              <AutoComplete
                className="w-full"
                options={bOptions}
                onSearch={onBathsSearch}
                onSelect={(value) => setBathsSearchTerm(value)}
                onChange={(value) => setBathsSearchTerm(value)}
                value={bathsSearchTerm}
              >
                <Input
                  size="large"
                  placeholder="Search by baths"
                  style={inputStyle}
                />
              </AutoComplete>
              <AutoComplete
                className="w-full"
                options={cityOptions}
                filterOption={(inputValue, option) =>
                  option?.value
                    ?.toLowerCase()
                    .indexOf(inputValue.toLowerCase()) !== -1
                }
                onSelect={(value) => setCitySearchTerm(value)}
                onChange={(value) => setCitySearchTerm(value)}
                value={citySearchTerm}
              >
                <Input
                  size="large"
                  placeholder="Search by city"
                  style={inputStyle}
                />
              </AutoComplete>
              <div className="grid grid-cols-2 md:grid-cols-2 gap-1 w-full max-w-8xl">
                <button
                  onClick={handleSearch}
                  className="bg-green-400 text-black px-10 py-1 rounded-lg sm:text-xl md:text-xl lg:text-4xl hover:bg-green-500 text-3xl font-semibold "
                  style={{ fontFamily: "Helvetica" }}
                >
                  Search
                </button>
                <button
                  onClick={handleClearSearch}
                  className="bg-green-400 text-black px-10 py-1 rounded-lg  sm:text-xl  md:text-xl lg:text-4xl hover:bg-green-500 text-3xl font-semibold "
                  style={{ fontFamily: "Helvetica" }}
                >
                  Clear
                </button>
              </div>
            </div>
            <div className="w-full max-w-7xl">
              {/* <p className="text-black">Price Range:</p> */}
              <PriceRangeSlider
                min={0}
                max={10000000}
                value={priceRange}
                onChange={setPriceRange}
              />
            </div>
          </div>
          {selectedCityData && (
            <div
              className="w-full max-w-4xl p-4 bg-gray-800 rounded-lg"
              style={{ fontFamily: "Helvetica" }}
            >
              <h2 className="text-xl font-semibold text-white mb-2">
                {selectedCityData.city}
              </h2>
              <p className="text-white mb-2 text-xl">
                {selectedCityData.description}
              </p>
              <div className="flex justify-between text-xl">
                <p className="text-white">
                  Average Price: {selectedCityData.average_price}
                </p>
                <p className="text-white">
                  Price per Sq Ft: {selectedCityData.sqft_price}
                </p>
              </div>
            </div>
          )}
          <div className="w-full h-px bg-zinc-800 my-2" />

          <div className="grid grid-cols-2">
            <div>
              <div
                className="grid grid-cols-1 gap-4 mx-auto lg:mx-0 md:grid-cols-2 lg:grid-cols-2"
                style={{ fontFamily: "Helvetica" }}
              >
                {filteredData.slice(0, displayCount).map((home, key) => (
                  <div
                    key={key}
                    className="grid grid-cols-1 gap-4 cursor-pointer"
                  >
                    <Card className="">
                      <Link href={home?.home_url} target="blank">
                        <div className="cursor-pointer w-full h-[200px] relative">
                          <Image
                            className="rounded-t-xl overflow-hidden object-cover"
                            src={home?.image_link}
                            alt={home?.address}
                            fill
                            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                          />
                        </div>
                        <div className="p-1 rounded-b-xl">
                          {home?.address ? (
                            <p className="text-2xl text-gray-300 truncate text-center">
                              {home?.address}
                            </p>
                          ) : (
                            <div>
                              <br></br>
                            </div>
                          )}
                          <div className="flex flex-row items-center justify-between mb-2">
                            <h1 className="text-2xl font-semibold bg-yellow-400 rounded-lg text-black px-1">
                              {home?.price}
                            </h1>
                            {home?.beds ? (
                              <span className="text-2xl bg-purple-400 text-black rounded-lg truncate px-2">
                                {home?.beds}
                              </span>
                            ) : (
                              <div></div>
                            )}
                            <span className="text-2xl bg-orange-400 text-black rounded-lg truncate px-2">
                              {home?.baths}
                            </span>
                            {home?.area ? (
                              <span className="text-2xl bg-lime-400 text-black rounded-lg truncate px-1">
                                {home?.area} sq ft
                              </span>
                            ) : (
                              <div></div>
                            )}
                          </div>

                          <div className="flex flex-row items-center justify-center space-x-3">
                            <h1 className="text-2xl bg-green-400 text-black px-2  rounded-lg truncate">
                              {home?.city}
                            </h1>
                            <h1 className="text-2xl bg-blue-400 text-black px-6 rounded-lg truncate">
                              {home?.country === "United Kingdom"
                                ? "UK"
                                : home?.country}
                            </h1>
                            <h1 className="text-2xl bg-red-400 text-black px-7 rounded-lg">
                              {home?.source}
                            </h1>
                          </div>
                        </div>
                      </Link>
                    </Card>
                  </div>
                ))}
              </div>
              <div className="w-full flex justify-center mt-8">
                {displayCount < filteredData.length && (
                  <p
                    onClick={() =>
                      setDisplayCount((prevCount) => prevCount + 60)
                    }
                    type="primary"
                    size="large"
                    className="text-green-400 hover:text-green-500 text-xl mb-10 hover:cursor-pointer font-semibold"
                    style={{ fontFamily: "Helvetica" }}
                  >
                    More data
                  </p>
                )}
              </div>
            </div>
            <div className="sticky top-[80px] h-[calc(100vh-80px)]">
              <MapView
                allData={allData}
                cityOptions={cityOptions}
                citySearchTerm={citySearchTerm}
              />
            </div>
          </div>
          <ScrollToTopButton />
        </div>
      ) : (
        <LoadingComponent />
      )}
    </div>
  );
};

export default MainPage;
