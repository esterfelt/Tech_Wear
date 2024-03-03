// TODO add new column after Catalog

import Logo from '../components/Logo'
import './Footer.scss'
import Join from '../components/Join'
import { NavLink } from 'react-router-dom'

function Footer() {
  return (
      <footer className="footer">
      <div className="footer-content">
        <Logo />
        <div className="footer-section">
          <nav className="catalog">
            <h4>Catalog</h4>
            <ul className='list'>
              <li><NavLink href="/">Home</NavLink></li>
              <li><NavLink href="/catalog">Catalog</NavLink></li>
              <li><NavLink href="/accessories">Accessories</NavLink></li>
              <li><NavLink href="/new">New</NavLink></li>
              <li><NavLink href="/about">About</NavLink></li>
            </ul>
          </nav>
        </div>
        
        <div className="footer-section">
          <div className="info">
            <h4>Info</h4>
            <ul className='list'>
              <li><a href="#">Behance</a></li>
              <li><a href="#">Dribbble</a></li>
              <li><a href="#">Pinterest</a></li>
              <li><a href="#">Youtube</a></li>
            </ul>
          </div>
        </div>
        <Join />
      </div>
    </footer>
  )
}

export default Footer