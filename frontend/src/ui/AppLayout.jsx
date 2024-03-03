import Header from "./Header";
import { Outlet } from "react-router";
import Footer from "./Footer";

function AppLayout() {
  return (
    <div>
      <Header />
      <div>
        <main>
          <Outlet />
        </main>
      <Footer />
      </div>
    </div>
  );
}

export default AppLayout;
