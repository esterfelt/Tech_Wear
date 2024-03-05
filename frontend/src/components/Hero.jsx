import './Hero.scss'

function Hero() {
  return (
    <div className="hero">
        <h1 className="hero_header">The Enigma Collection: Unveiling CyberStyle Mystique</h1>
        <div className='hero_video'>
        <video src="../video/hero.MP4" autoPlay loop muted width='1200px' height='500px'></video>
        </div>
    </div>
  )
}

export default Hero