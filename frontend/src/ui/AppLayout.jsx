import React from "react";
import Header from "./Header";
import { Outlet } from "react-router";

function AppLayout() {
  return (
    <div>
      <Header />
      <div>
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
