import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

function Layout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="content-column">
        <TopBar />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

Layout.displayName = "Layout";

export default Layout;
