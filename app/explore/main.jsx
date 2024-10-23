"use client";
import React, { useState, useEffect, useMemo } from "react";
import { Card } from "@/app/components/card";
import { LoadingComponent } from "@/app/components/loading";
import Image from "next/image";
import Link from "next/link";
import { useData } from "../hooks/useData";
import { AutoComplete, Input, Button, DatePicker, Slider } from "antd";
import PriceRangeSlider from "@/app/components/slider";
import axios from "axios";
import moment from "moment";

const { RangePicker } = DatePicker;

export const MainPage = () => {
  const { homeData, stateData, loading } = useData();

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
  console.log("sn", stateData?.length);
  console.log("sn", stateData?.slice(0, 3));

  const cityOptions = Array.from(
    new Set(
      homeData
        .map((home) => home?.city)
        .filter((city) => city && city.trim() !== "")
    )
  )
    .map((city) => ({ value: city, label: city }))
    .sort((a, b) => a.label.localeCompare(b.label));

  const handleSearch = () => {
    const filtered = homeData.filter((home) => {
      const price = parseFloat(home?.price?.replace(/[^0-9.-]+/g, ""));
      return (
        (bedsSearchTerm === "" ||
          home?.beds?.toLowerCase().includes(bedsSearchTerm.toLowerCase())) &&
        (bathsSearchTerm === "" ||
          home?.baths?.toLowerCase().includes(bathsSearchTerm.toLowerCase())) &&
        (citySearchTerm === "" ||
          home?.city?.toLowerCase().includes(citySearchTerm.toLowerCase())) &&
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
  console.log("=============citySearchTerm===============", citySearchTerm);
  console.log("===========selectedCityData==============", selectedCityData);

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
    return Array.from(new Set(homeData.map((home) => home?.beds))).map(
      (beds) => ({
        value: beds,
        label: beds,
      })
    );
  }, [homeData]);

  const bathsOptions = useMemo(() => {
    return Array.from(new Set(homeData.map((home) => home?.baths))).map(
      (baths) => ({
        value: baths,
        label: baths,
      })
    );
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
    height: "40px",
    fontSize: "16px",
  };

  return (
    <div className="min-h-screen bg-black font-helvetica">
      {!loading ? (
        <div className="px-6 pt-[80px] mx-auto max-w-[100rem] lg:px-8">
          <div className="flex flex-col items-center w-full space-y-4 p-4 rounded-lg shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-4xl">
              <AutoComplete
                className="w-full"
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
            </div>
            <div className="w-full max-w-4xl">
              <p className="text-white">Price Range:</p>
              <PriceRangeSlider
                min={0}
                max={10000000}
                value={priceRange}
                onChange={setPriceRange}
              />
            </div>

            <div className="flex space-x-4">
              <Button
                onClick={handleSearch}
                type="default"
                size="large"
                className="bg-green-600 text-white px-8"
                style={{ fontFamily: "Helvetica" }}
              >
                Search
              </Button>
              <Button
                onClick={handleClearSearch}
                type="default"
                size="large"
                className="bg-green-600 text-white px-8"
                style={{ fontFamily: "Helvetica" }}
              >
                Clear
              </Button>
            </div>
          </div>
          {selectedCityData && (
            <div
              className="w-full max-w-4xl p-4 bg-gray-800 rounded-lg"
              style={{ fontFamily: "Helvetica" }}
            >
              <h2 className="text-xl font-semibold text-white mb-2">
                {selectedCityData.city}, {selectedCityData.state}
              </h2>
              <p className="text-gray-300 mb-2 text-xl">
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
          <div className="w-full h-px bg-zinc-800 my-4" />

          <div
            className="grid grid-cols-1 gap-4 mx-auto lg:mx-0 md:grid-cols-2 lg:grid-cols-4"
            style={{ fontFamily: "Helvetica" }}
          >
            {filteredData.slice(0, displayCount).map((home, key) => (
              <div key={key} className="grid grid-cols-1 gap-4 cursor-pointer">
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
                    <div className="p-2 rounded-b-xl">
                      <div className="flex flex-row items-center justify-between">
                        <h1 className="text-2xl font-semibold text-white">
                          {home?.price}
                        </h1>
                        {home?.beds ? (
                          <span className="text-md bg-green-600 text-white px-1 rounded-full">
                            {home?.beds}
                          </span>
                        ) : (
                          <div></div>
                        )}
                        <span className="text-md bg-green-600 text-white px-1 rounded-full">
                          {home?.baths}
                        </span>
                        {home?.area ? (
                          <span className="text-md bg-green-600 text-white px-1 rounded-full">
                            {home?.area} sq ft
                          </span>
                        ) : (
                          <div></div>
                        )}
                      </div>
                      {home?.address ? (
                        <p className="text-xl text-gray-300 truncate">
                          {home?.address}
                        </p>
                      ) : (
                        <div>
                          <br></br>
                        </div>
                      )}
                      <div className="flex flex-row items-center justify-center space-x-5">
                        <h1 className="text-lg bg-green-600 text-white px-2  rounded-full ">
                          {home?.city}
                        </h1>
                        <h1 className="text-lg bg-green-600 text-white px-2 rounded-full">
                          {home?.country}
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
                onClick={() => setDisplayCount((prevCount) => prevCount + 60)}
                type="primary"
                size="large"
                className="text-white hover:text-green-500 text-xl mb-10 hover:cursor-pointer"
              >
                More data
              </p>
            )}
          </div>
        </div>
      ) : (
        <LoadingComponent />
      )}
    </div>
  );
};

export default MainPage;
