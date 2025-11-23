// // import React, { useEffect, useState } from "react";
// // import axios from "axios";
// // import { motion } from "framer-motion";
// // import GeoMap from "../components/GeoMap";
// // import GeoFilter from "../components/GeoFilter";
// // import NewsCard from "../components/NewsCard";
// //
// // function GeoDashboard() {
// //   const [articles, setArticles] = useState([]);
// //   const [filteredArticles, setFilteredArticles] = useState([]);
// //   const [loading, setLoading] = useState(true);
// //   const [stats, setStats] = useState({
// //     totalArticles: 0,
// //     geoTaggedCount: 0,
// //     coverage: 0,
// //     uniqueLocations: 0,
// //   });
// //   const [locations, setLocations] = useState([]);
// //   const [showHeatmap, setShowHeatmap] = useState(true); // Heatmap toggle
// //
// //   useEffect(() => {
// //     const fetchData = async () => {
// //       try {
// //         setLoading(true);
// //         const response = await axios.get("http://127.0.0.1:8000/news_stored_full");
// //         const allArticles = response.data || [];
// //
// //         setArticles(allArticles);
// //         setFilteredArticles(allArticles);
// //
// //         // Calculate geo-tagged stats
// //         const geoTagged = allArticles.filter((a) => a.lat && a.lon);
// //         const locationList = [
// //           ...new Set(
// //             allArticles.map((a) => a.location).filter((loc) => loc && loc.trim())
// //           ),
// //         ].sort();
// //
// //         setLocations(locationList);
// //
// //         setStats({
// //           totalArticles: allArticles.length,
// //           geoTaggedCount: geoTagged.length,
// //           coverage:
// //             allArticles.length > 0
// //               ? Math.round((geoTagged.length / allArticles.length) * 100)
// //               : 0,
// //           uniqueLocations: locationList.length,
// //         });
// //
// //         setLoading(false);
// //       } catch (error) {
// //         console.error("Error fetching geo data:", error);
// //         setLoading(false);
// //       }
// //     };
// //
// //     fetchData();
// //     const interval = setInterval(fetchData, 300000);
// //     return () => clearInterval(interval);
// //   }, []);
// //
// //   // When filter changes
// //   const handleGeoFilter = (filtered) => {
// //     setFilteredArticles(filtered);
// //   };
// //
// //   if (loading) {
// //     return (
// //       <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
// //         <div className="text-center">
// //           <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
// //           <p className="text-gray-600 text-lg font-medium">Loading geo data...</p>
// //         </div>
// //       </div>
// //     );
// //   }
// //
// //   return (
// //     <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6">
// //       <div className="max-w-7xl mx-auto">
// //         {/* Header */}
// //         <motion.div
// //           className="text-center mb-12"
// //           initial={{ opacity: 0, y: -20 }}
// //           animate={{ opacity: 1, y: 0 }}
// //           transition={{ duration: 0.6 }}
// //         >
// //           <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">
// //             Geo-Tagging Dashboard
// //           </h1>
// //           <p className="text-lg text-gray-600">
// //             Real-time geographic insights from news articles
// //           </p>
// //         </motion.div>
// //
// //         {/* Statistics Grid */}
// //         <motion.div
// //           className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
// //           initial={{ opacity: 0 }}
// //           animate={{ opacity: 1 }}
// //           transition={{ duration: 0.6, staggerChildren: 0.1 }}
// //         >
// //           {/* Total Articles Card */}
// //           <StatisticCard
// //             color="blue"
// //             value={stats.totalArticles}
// //             title="Total Articles"
// //             description="Articles processed"
// //             icon={
// //               <svg
// //                 className="w-6 h-6 text-blue-600"
// //                 fill="none"
// //                 stroke="currentColor"
// //                 viewBox="0 0 24 24"
// //               >
// //                 <path
// //                   strokeLinecap="round"
// //                   strokeLinejoin="round"
// //                   strokeWidth={2}
// //                   d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
// //                 />
// //               </svg>
// //             }
// //           />
// //
// //           {/* Geo-Tagged Articles Card */}
// //           <StatisticCard
// //             color="green"
// //             value={stats.geoTaggedCount}
// //             title="Geo-Tagged"
// //             description="With location data"
// //             icon={
// //               <svg
// //                 className="w-6 h-6 text-green-600"
// //                 fill="currentColor"
// //                 viewBox="0 0 24 24"
// //               >
// //                 <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
// //               </svg>
// //             }
// //           />
// //
// //           {/* Coverage Card */}
// //           <StatisticCard
// //             color="purple"
// //             value={stats.coverage + "%"}
// //             title="Coverage"
// //             description="Location coverage"
// //             icon={
// //               <svg
// //                 className="w-6 h-6 text-purple-600"
// //                 fill="none"
// //                 stroke="currentColor"
// //                 viewBox="0 0 24 24"
// //               >
// //                 <path
// //                   strokeLinecap="round"
// //                   strokeLinejoin="round"
// //                   strokeWidth={2}
// //                   d="M13 10V3L4 14h7v7l9-11h-7z"
// //                 />
// //               </svg>
// //             }
// //             progress={stats.coverage}
// //           />
// //
// //           {/* Unique Locations Card */}
// //           <StatisticCard
// //             color="orange"
// //             value={stats.uniqueLocations}
// //             title="Locations"
// //             description="Unique locations"
// //             icon={
// //               <svg
// //                 className="w-6 h-6 text-orange-600"
// //                 fill="none"
// //                 stroke="currentColor"
// //                 viewBox="0 0 24 24"
// //               >
// //                 <path
// //                   strokeLinecap="round"
// //                   strokeLinejoin="round"
// //                   strokeWidth={2}
// //                   d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
// //                 />
// //                 <path
// //                   strokeLinecap="round"
// //                   strokeLinejoin="round"
// //                   strokeWidth={2}
// //                   d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
// //                 />
// //               </svg>
// //             }
// //           />
// //         </motion.div>
// //
// //         {/* Map Section */}
// //         {stats.geoTaggedCount > 0 && (
// //           <motion.div
// //             className="bg-white rounded-2xl shadow-lg overflow-hidden mb-12"
// //             initial={{ opacity: 0, y: 20 }}
// //             animate={{ opacity: 1, y: 0 }}
// //             transition={{ duration: 0.6, delay: 0.3 }}
// //           >
// //             <div className="p-8 border-b border-gray-200 flex items-center justify-between">
// //               <div>
// //                 <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
// //                   🗺️ Geographic Distribution
// //                 </h2>
// //                 <p className="text-gray-600 mt-2">
// //                   Interactive map showing article locations worldwide
// //                 </p>
// //               </div>
// //               <div>
// //                 <label className="text-sm font-medium mr-2">Heatmap</label>
// //                 <input
// //                   type="checkbox"
// //                   checked={showHeatmap}
// //                   onChange={() => setShowHeatmap((v) => !v)}
// //                   className="toggle-checkbox"
// //                   style={{ transform: "scale(1.2)", cursor: "pointer" }}
// //                 />
// //               </div>
// //             </div>
// //             <div className="overflow-hidden">
// //               <GeoMap articles={filteredArticles} heatmap={showHeatmap} />
// //             </div>
// //           </motion.div>
// //         )}
// //
// //         {/* Filter & News Section */}
// //         <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 mb-12">
// //           {/* Filter Sidebar */}
// //           <motion.div
// //             className="lg:col-span-1"
// //             initial={{ opacity: 0, x: -20 }}
// //             animate={{ opacity: 1, x: 0 }}
// //             transition={{ duration: 0.6, delay: 0.4 }}
// //           >
// //             <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-20">
// //               <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
// //                 📍 Filter News
// //               </h3>
// //               <GeoFilter
// //                 articles={articles} // Prop drill articles list
// //                 onFilterChange={handleGeoFilter}
// //               />
// //             </div>
// //           </motion.div>
// //
// //           {/* Articles Grid */}
// //           <motion.div
// //             className="lg:col-span-3"
// //             initial={{ opacity: 0, x: 20 }}
// //             animate={{ opacity: 1, x: 0 }}
// //             transition={{ duration: 0.6, delay: 0.4 }}
// //           >
// //             <div className="mb-6">
// //               <h3 className="text-2xl font-bold text-gray-900 mb-2">
// //                 News Articles
// //               </h3>
// //               <p className="text-gray-600">
// //                 Showing {filteredArticles.length} of {articles.length} articles
// //               </p>
// //             </div>
// //
// //             {filteredArticles.length > 0 ? (
// //               <div className="grid gap-6">
// //                 {filteredArticles.map((article, idx) => (
// //                   <motion.div
// //                     key={idx}
// //                     initial={{ opacity: 0, y: 20 }}
// //                     animate={{ opacity: 1, y: 0 }}
// //                     transition={{ duration: 0.4, delay: idx * 0.05 }}
// //                   >
// //                     <NewsCard article={article} />
// //                   </motion.div>
// //                 ))}
// //               </div>
// //             ) : (
// //               <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
// //                 <svg
// //                   className="w-16 h-16 text-gray-400 mx-auto mb-4"
// //                   fill="none"
// //                   stroke="currentColor"
// //                   viewBox="0 0 24 24"
// //                 >
// //                   <path
// //                     strokeLinecap="round"
// //                     strokeLinejoin="round"
// //                     strokeWidth={1.5}
// //                     d="M20 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"
// //                   />
// //                 </svg>
// //                 <h3 className="text-lg font-semibold text-gray-900 mb-2">
// //                   No articles found
// //                 </h3>
// //                 <p className="text-gray-600">
// //                   Try selecting a different location or check back later
// //                 </p>
// //               </div>
// //             )}
// //           </motion.div>
// //         </div>
// //
// //         {/* Footer Stats */}
// //         <motion.div
// //           className="bg-white rounded-2xl shadow-lg p-8"
// //           initial={{ opacity: 0, y: 20 }}
// //           animate={{ opacity: 1, y: 0 }}
// //           transition={{ duration: 0.6, delay: 0.5 }}
// //         >
// //           <h3 className="text-xl font-bold text-gray-900 mb-6">📊 Quick Insights</h3>
// //           <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
// //             <QuickStat
// //               icon="📈"
// //               value={
// //                 stats.geoTaggedCount > 0
// //                   ? `${Math.round((stats.geoTaggedCount / stats.totalArticles) * 100)}% Accuracy`
// //                   : "No Data"
// //               }
// //               description="Location extraction success rate"
// //             />
// //             <QuickStat
// //               icon="🌐"
// //               value={`${stats.uniqueLocations} Regions`}
// //               description="News coverage across locations"
// //             />
// //             <QuickStat
// //               icon="🎯"
// //               value={`${stats.totalArticles} Articles`}
// //               description="Total processed in database"
// //             />
// //           </div>
// //         </motion.div>
// //       </div>
// //     </div>
// //   );
// // }
// //
// // // --- Reusable subcomponents (StatisticCard, QuickStat) ---
// // function StatisticCard({ color, value, title, description, icon, progress }) {
// //   return (
// //     <motion.div
// //       className={`bg-white rounded-2xl shadow-lg hover:shadow-xl p-8 border-l-4 border-${color}-500`}
// //       whileHover={{ translateY: -5 }}
// //       transition={{ type: "spring", stiffness: 200 }}
// //     >
// //       <div className="flex items-center justify-between mb-4">
// //         <h3 className="text-gray-600 font-semibold text-sm uppercase tracking-wider">
// //           {title}
// //         </h3>
// //         <div className={`bg-${color}-100 p-3 rounded-full`}>{icon}</div>
// //       </div>
// //       <div className={`text-4xl font-bold text-${color}-600 mb-2`}>
// //         {value}
// //       </div>
// //       <p className="text-gray-500 text-sm">{description}</p>
// //       {progress !== undefined && (
// //         <div className="mt-4 bg-purple-100 rounded-full h-2 overflow-hidden">
// //           <motion.div
// //             className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full rounded-full"
// //             initial={{ width: 0 }}
// //             animate={{ width: `${progress}%` }}
// //             transition={{ duration: 1, delay: 0.3 }}
// //           />
// //         </div>
// //       )}
// //     </motion.div>
// //   );
// // }
// //
// // function QuickStat({ icon, value, description }) {
// //   return (
// //     <div className="flex items-start gap-4">
// //       <div className="bg-blue-100 p-3 rounded-lg flex-shrink-0">
// //         <span className="text-2xl">{icon}</span>
// //       </div>
// //       <div>
// //         <p className="font-semibold text-gray-900">{value}</p>
// //         <p className="text-sm text-gray-600">{description}</p>
// //       </div>
// //     </div>
// //   );
// // }
// //
// // export default GeoDashboard;
//
// // src/pages/GeoDashboard.js
//
// import React, { useEffect, useState } from "react";
// import axios from "axios";
// import { motion } from "framer-motion";
// import GeoMap from "../components/GeoMap";
// import GeoFilter from "../components/GeoFilter";
// import NewsCard from "../components/NewsCard";
//
// // Adjust this to your backend base URL or read from env
// const API_BASE =
//   process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";
//
// function GeoDashboard() {
//   const [articles, setArticles] = useState([]);
//   const [filteredArticles, setFilteredArticles] = useState([]);
//   const [loading, setLoading] = useState(true);
//
//   const [stats, setStats] = useState({
//     totalArticles: 0,
//     geoTaggedCount: 0,
//     coverage: 0,
//     uniqueLocations: 0,
//     missingGeo: 0,
//   });
//
//   const [locations, setLocations] = useState([]);
//   const [showHeatmap, setShowHeatmap] = useState(true);
//
//   // NEW: heatmap points + simple filters for days/topic
//   const [heatPoints, setHeatPoints] = useState([]);
//   const [heatLoading, setHeatLoading] = useState(false);
//   const [heatError, setHeatError] = useState(null);
//   const [selectedDays, setSelectedDays] = useState(7);     // you can later connect this to a UI control
//   const [selectedTopic, setSelectedTopic] = useState("");  // same
//
//   // Fetch heat points from /geo/heat
//   useEffect(() => {
//     const fetchHeatPoints = async () => {
//       try {
//         setHeatLoading(true);
//         setHeatError(null);
//
//         const params = new URLSearchParams();
//         params.set("days", selectedDays || 7);
//         if (selectedTopic) params.set("topic", selectedTopic);
//
//         const res = await fetch(`${API_BASE}/geo/heat?` + params.toString());
//         if (!res.ok) {
//           throw new Error(`HTTP ${res.status}`);
//         }
//         const data = await res.json();
//         setHeatPoints(data || []);
//       } catch (err) {
//         console.error("Failed to load geo heat points", err);
//         setHeatError(String(err));
//       } finally {
//         setHeatLoading(false);
//       }
//     };
//
//     fetchHeatPoints();
//   }, [selectedDays, selectedTopic]);
//
//   // Fetch all stored articles (GDELT + others)
//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         setLoading(true);
//
//         const response = await axios.get(
//           `${API_BASE}/news_stored_full`
//         );
//         const allArticles = response.data || [];
//
//         // setArticles(allArticles);
//         setFilteredArticles(allArticles);
//
//         const geoTagged = allArticles.filter(
//           (a) =>
//             a &&
//             a.lat !== null &&
//             a.lat !== undefined &&
//             a.lon !== null &&
//             a.lon !== undefined
//         );
//
//         const locationList = [
//           ...new Set(
//             allArticles
//               .map((a) => a.location)
//               .filter((loc) => loc && typeof loc === "string" && loc.trim())
//           ),
//         ].sort();
//
//         const missingGeoCount = allArticles.length - geoTagged.length;
//
//         setLocations(locationList);
//         setStats({
//           totalArticles: allArticles.length,
//           geoTaggedCount: geoTagged.length,
//           coverage:
//             allArticles.length > 0
//               ? Math.round((geoTagged.length / allArticles.length) * 100)
//               : 0,
//           uniqueLocations: locationList.length,
//           missingGeo: missingGeoCount,
//         });
//
//         setLoading(false);
//       } catch (error) {
//         console.error("Error fetching geo data:", error);
//         setLoading(false);
//       }
//     };
//
//     fetchData();
//     const interval = setInterval(fetchData, 300000);
//     return () => clearInterval(interval);
//   }, []);
//
//   const handleGeoFilter = (filtered) => {
//     setFilteredArticles(filtered);
//   };
//
//   if (loading) {
//     return (
//       <div className="min-h-screen flex items-center justify-center bg-slate-50">
//         <div className="text-center space-y-4">
//           <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500 mx-auto" />
//           <h2 className="text-xl font-semibold text-slate-800">
//             Loading geo data...
//           </h2>
//           <p className="text-sm text-slate-500">
//             Real-time geographic insights from news articles
//           </p>
//         </div>
//       </div>
//     );
//   }
//
//   return (
//     <div className="min-h-screen bg-slate-50 flex">
//       <div className="w-0 md:w-64" />
//
//       <main className="flex-1 p-4 md:p-8">
//         {/* Header */}
//         <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
//           <div>
//             <h1 className="text-2xl md:text-3xl font-bold text-slate-900">
//               Geo-Tagging Dashboard
//             </h1>
//             <p className="text-sm text-slate-500">
//               Real-time geographic insights from news articles
//             </p>
//           </div>
//
//           <div className="flex items-center gap-3">
//             <label className="flex items-center gap-2 text-sm text-slate-600">
//               <input
//                 type="checkbox"
//                 checked={showHeatmap}
//                 onChange={(e) => setShowHeatmap(e.target.checked)}
//                 className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
//               />
//               <span>Heatmap</span>
//             </label>
//           </div>
//         </div>
//
//         {/* Stats cards */}
//         <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
//           <StatCard
//             title="Total Articles"
//             value={stats.totalArticles}
//             description="Articles processed"
//           />
//           <StatCard
//             title="Geo-Tagged"
//             value={stats.geoTaggedCount}
//             description="With coordinate data"
//           />
//           <StatCard
//             title="Coverage"
//             value={`${stats.coverage}%`}
//             description="Location coverage"
//             progress={stats.coverage}
//           />
//           <StatCard
//             title="Unique Locations"
//             value={stats.uniqueLocations}
//             description="Distinct place names"
//           />
//           <StatCard
//             title="Missing Geo"
//             value={stats.missingGeo}
//             description="Articles without lat/lon"
//           />
//         </div>
//
//         <div className="mb-6">
//           <p className="text-xs text-slate-500">
//             Missing geo for {stats.missingGeo} articles (no lat/lon after
//             GDELT + NER geo-tagging).
//           </p>
//         </div>
//
//         <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
//           <div className="xl:col-span-2 space-y-4">
//             <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
//               <div className="border-b border-slate-100 px-4 py-3 flex items-center justify-between">
//                 <div className="flex items-center gap-2">
//                   <span className="inline-flex items-center justify-center h-7 w-7 rounded-full bg-indigo-50 text-indigo-600 text-sm">
//                     🌍
//                   </span>
//                   <div>
//                     <h2 className="text-sm font-semibold text-slate-800">
//                       Geographic Distribution
//                     </h2>
//                     <p className="text-xs text-slate-500">
//                       Interactive map showing article locations worldwide
//                     </p>
//                   </div>
//                 </div>
//               </div>
//
//               <div className="h-[420px] md:h-[480px]">
//                 <GeoMap
//                   articles={filteredArticles}
//                   showHeatmap={showHeatmap}
//                   heatPoints={heatPoints}        // NEW: pass points to map
//                   heatLoading={heatLoading}
//                   heatError={heatError}
//                 />
//               </div>
//             </section>
//
//             <GeoFilter
//               allArticles={articles}
//               onFilterChange={handleGeoFilter}
//               locations={locations}
//             />
//           </div>
//
//           <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
//             <div className="border-b border-slate-100 px-4 py-3">
//               <h2 className="text-sm font-semibold text-slate-800">
//                 News Articles
//               </h2>
//               <p className="text-xs text-slate-500">
//                 Showing {filteredArticles.length} of {articles.length} articles
//               </p>
//             </div>
//
//             <div className="overflow-y-auto max-h-[520px] divide-y divide-slate-100">
//               {filteredArticles.length === 0 ? (
//                 <div className="p-4 text-xs text-slate-500">
//                   No articles match the selected filters. Try selecting a
//                   different location or check back later.
//                 </div>
//               ) : (
//                 filteredArticles.map((article, idx) => (
//                   <NewsCard
//                     key={article.id || article.url || idx}
//                     article={article}
//                   />
//                 ))
//               )}
//             </div>
//           </section>
//         </div>
//       </main>
//     </div>
//   );
// }
//
// function StatCard({ title, value, description, progress }) {
//   return (
//     <motion.div
//       className="bg-white rounded-2xl shadow-sm border border-slate-100 p-4 flex flex-col justify-between"
//       initial={{ opacity: 0, y: 8 }}
//       animate={{ opacity: 1, y: 0 }}
//       transition={{ duration: 0.2 }}
//     >
//       <div className="flex items-center justify-between mb-2">
//         <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
//           {title}
//         </p>
//       </div>
//       <div className="mb-1">
//         <p className="text-xl font-semibold text-slate-900">{value}</p>
//       </div>
//       <p className="text-xs text-slate-500 mb-2">{description}</p>
//       {progress !== undefined && (
//         <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
//           <div
//             className="h-full bg-indigo-500 rounded-full"
//             style={{ width: `${progress}%` }}
//           />
//         </div>
//       )}
//     </motion.div>
//   );
// }
//
// export default GeoDashboard;







import React, { useEffect, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import GeoMap from "../components/GeoMap";
import GeoFilter from "../components/GeoFilter";
import NewsCard from "../components/NewsCard";

function GeoDashboard() {
  const [articles, setArticles] = useState([]);
  const [filteredArticles, setFilteredArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalArticles: 0,
    geoTaggedCount: 0,
    coverage: 0,
    uniqueLocations: 0,
  });
  const [locations, setLocations] = useState([]);
  const [showHeatmap, setShowHeatmap] = useState(true); // Heatmap toggle

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axios.get("http://127.0.0.1:8000/news_stored_full");
        const allArticles = response.data || [];

        setArticles(allArticles);
        setFilteredArticles(allArticles);

        // Calculate geo-tagged stats
        const geoTagged = allArticles.filter((a) => a.lat && a.lon);
        const locationList = [
          ...new Set(
            allArticles.map((a) => a.location).filter((loc) => loc && loc.trim())
          ),
        ].sort();

        setLocations(locationList);

        setStats({
          totalArticles: allArticles.length,
          geoTaggedCount: geoTagged.length,
          coverage:
            allArticles.length > 0
              ? Math.round((geoTagged.length / allArticles.length) * 100)
              : 0,
          uniqueLocations: locationList.length,
        });

        setLoading(false);
      } catch (error) {
        console.error("Error fetching geo data:", error);
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 300000);
    return () => clearInterval(interval);
  }, []);

  // When filter changes
  const handleGeoFilter = (filtered) => {
    setFilteredArticles(filtered);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg font-medium">Loading geo data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">
            Geo-Tagging Dashboard
          </h1>
          <p className="text-lg text-gray-600">
            Real-time geographic insights from news articles
          </p>
        </motion.div>

        {/* Statistics Grid */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, staggerChildren: 0.1 }}
        >
          {/* Total Articles Card */}
          <StatisticCard
            color="blue"
            value={stats.totalArticles}
            title="Total Articles"
            description="Articles processed"
            icon={
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            }
          />

          {/* Geo-Tagged Articles Card */}
          <StatisticCard
            color="green"
            value={stats.geoTaggedCount}
            title="Geo-Tagged"
            description="With location data"
            icon={
              <svg
                className="w-6 h-6 text-green-600"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
              </svg>
            }
          />

          {/* Coverage Card */}
          <StatisticCard
            color="purple"
            value={stats.coverage + "%"}
            title="Coverage"
            description="Location coverage"
            icon={
              <svg
                className="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            }
            progress={stats.coverage}
          />

          {/* Unique Locations Card */}
          <StatisticCard
            color="orange"
            value={stats.uniqueLocations}
            title="Locations"
            description="Unique locations"
            icon={
              <svg
                className="w-6 h-6 text-orange-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            }
          />
        </motion.div>

        {/* Map Section */}
        {stats.geoTaggedCount > 0 && (
          <motion.div
            className="bg-white rounded-2xl shadow-lg overflow-hidden mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <div className="p-8 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                  🗺️ Geographic Distribution
                </h2>
                <p className="text-gray-600 mt-2">
                  Interactive map showing article locations worldwide
                </p>
              </div>
              <div>
                <label className="text-sm font-medium mr-2">Heatmap</label>
                <input
                  type="checkbox"
                  checked={showHeatmap}
                  onChange={() => setShowHeatmap((v) => !v)}
                  className="toggle-checkbox"
                  style={{ transform: "scale(1.2)", cursor: "pointer" }}
                />
              </div>
            </div>
            <div className="overflow-hidden">
              <GeoMap articles={filteredArticles} heatmap={showHeatmap} />
            </div>
          </motion.div>
        )}

        {/* Filter & News Section */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 mb-12">
          {/* Filter Sidebar */}
          <motion.div
            className="lg:col-span-1"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-20">
              <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                📍 Filter News
              </h3>
              <GeoFilter
                articles={articles} // Prop drill articles list
                onFilterChange={handleGeoFilter}
              />
            </div>
          </motion.div>

          {/* Articles Grid */}
          <motion.div
            className="lg:col-span-3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <div className="mb-6">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                News Articles
              </h3>
              <p className="text-gray-600">
                Showing {filteredArticles.length} of {articles.length} articles
              </p>
            </div>

            {filteredArticles.length > 0 ? (
              <div className="grid gap-6">
                {filteredArticles.map((article, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: idx * 0.05 }}
                  >
                    <NewsCard article={article} />
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
                <svg
                  className="w-16 h-16 text-gray-400 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M20 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"
                  />
                </svg>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No articles found
                </h3>
                <p className="text-gray-600">
                  Try selecting a different location or check back later
                </p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Footer Stats */}
        <motion.div
          className="bg-white rounded-2xl shadow-lg p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <h3 className="text-xl font-bold text-gray-900 mb-6">📊 Quick Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <QuickStat
              icon="📈"
              value={
                stats.geoTaggedCount > 0
                  ? `${Math.round((stats.geoTaggedCount / stats.totalArticles) * 100)}% Accuracy`
                  : "No Data"
              }
              description="Location extraction success rate"
            />
            <QuickStat
              icon="🌐"
              value={`${stats.uniqueLocations} Regions`}
              description="News coverage across locations"
            />
            <QuickStat
              icon="🎯"
              value={`${stats.totalArticles} Articles`}
              description="Total processed in database"
            />
          </div>
        </motion.div>
      </div>
    </div>
  );
}

// --- Reusable subcomponents (StatisticCard, QuickStat) ---
function StatisticCard({ color, value, title, description, icon, progress }) {
  return (
    <motion.div
      className={`bg-white rounded-2xl shadow-lg hover:shadow-xl p-8 border-l-4 border-${color}-500`}
      whileHover={{ translateY: -5 }}
      transition={{ type: "spring", stiffness: 200 }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-gray-600 font-semibold text-sm uppercase tracking-wider">
          {title}
        </h3>
        <div className={`bg-${color}-100 p-3 rounded-full`}>{icon}</div>
      </div>
      <div className={`text-4xl font-bold text-${color}-600 mb-2`}>
        {value}
      </div>
      <p className="text-gray-500 text-sm">{description}</p>
      {progress !== undefined && (
        <div className="mt-4 bg-purple-100 rounded-full h-2 overflow-hidden">
          <motion.div
            className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 1, delay: 0.3 }}
          />
        </div>
      )}
    </motion.div>
  );
}

function QuickStat({ icon, value, description }) {
  return (
    <div className="flex items-start gap-4">
      <div className="bg-blue-100 p-3 rounded-lg flex-shrink-0">
        <span className="text-2xl">{icon}</span>
      </div>
      <div>
        <p className="font-semibold text-gray-900">{value}</p>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </div>
  );
}

export default GeoDashboard;