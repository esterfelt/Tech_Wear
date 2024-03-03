import './Carousel.scss';
import Arrows from '../ui/Arrows';
import Item from './Item';

import {data} from '../utils/data';
import { useState } from 'react';
export default function Carousel() {
  const carouselData = data.slice(4,7)
  const [currentIndex, setCurrentIndex] = useState(0)
    // HERE SHOULD BE STATE THAT I WILL PASS TO ARROWS
    const nextSlide = () => {
      setCurrentIndex((prevIndex) =>
        prevIndex === carouselData.length - 1 ? 0 : prevIndex + 1
      );
    };
  
    const prevSlide = () => {
      setCurrentIndex((prevIndex) =>
        prevIndex === 0 ? carouselData.length - 1 : prevIndex - 1
      )};
  return (
    <div className='carousel'>
    <div className='carousel-images'>
      {carouselData.map((item, index)=>(
        <Item 
          key={index} 
          image={item.image} 
          title={item.title} 
          price={item.price}
          active={index === currentIndex}
        />
      ))}
    </div>
      <Arrows prevSlide={ prevSlide } nextSlide={ nextSlide } />
    </div>
  )
}