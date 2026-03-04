import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Home from './pages/Home'
import App from './App'
import './index.css'

// 1. Define your routes in an array
const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
    // errorElement: <ErrorPage />, // Optional: Catch-all for 404s
  },
  {
    path: "/upload",
    element: <div className="p-10">Upload your receipt here!</div>, // page component goes here
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* 2. Provide the router to your app */}
    <RouterProvider router={router} />
  </React.StrictMode>,
)