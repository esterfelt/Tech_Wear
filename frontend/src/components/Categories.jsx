// using BEM
import "./Categories.scss";

import React from "react";
function Categories() {
  return (
    <div className="categories container">
      <h3 className="categories__title header">/main categories</h3>
      <div className="nav">
        <img
          src="/img/image 57.jpg"
          alt="black shirt with white stripes"
          className="nav__img"
        />
        <ul className="nav__list">
          <li className="nav__item">
            <a href="#">01 pants</a>
          </li>
          <li className="nav__item">
            <a href="#">02 jacket</a>
          </li>
          <li className="nav__item">
            <a href="#">03 hoodie</a>
          </li>
          <li className="nav__item">
            <a href="#">04 shirts</a>
          </li>
          <li className="nav__item">
            <a href="#">05 poncho</a>
          </li>
          <li className="nav__item">
            <a href="#">06 bag</a>
          </li>
          <li className="nav__item">
            <a href="#">07 mask</a>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Categories;
