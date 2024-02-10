import React from "react";
import { NavLink } from "react-router-dom";

import "./Header.scss";
function Header() {
  return (
    <header className="header-main">
      <div className="header-main__pages">
        <NavLink to="/">Home</NavLink>
        <NavLink to="/catalog">Catalog</NavLink>
        <NavLink to="/accessories">Accessories</NavLink>
        <NavLink to="/new">New</NavLink>
        <NavLink to="/about">About</NavLink>
      </div>
      <div className="logo">
        <NavLink to="/">
          <img src="your_logo_url" alt="Logo" />
        </NavLink>
      </div>
      <div className="header-main__helpers">
        <NavLink to="/search">Search</NavLink>
        <NavLink to="/authorization">Authorization</NavLink>
        <NavLink to="/cart">Cart</NavLink>
      </div>
    </header>
  );
}

export default Header;
