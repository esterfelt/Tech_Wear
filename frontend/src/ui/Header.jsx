import { NavLink } from "react-router-dom";
import Logo from "../components/Logo";

import "./Header.scss";
function Header() {
  return (
    <header className="header-main">
      <div className="header-main_pages">
        <NavLink to="/">Home</NavLink>
        <NavLink to="/catalog">Catalog</NavLink>
        <NavLink to="/accessories">Accessories</NavLink>
        <NavLink to="/new">New</NavLink>
        <NavLink to="/about">About</NavLink>
      </div>
      <Logo />
      <div className="header-main_helpers">
        <NavLink to="/search">Search</NavLink>
        <NavLink to="/authorization">Authorization</NavLink>
        <NavLink to="/cart">Bag(0)</NavLink>
      </div>
    </header>
  );
}

export default Header;
