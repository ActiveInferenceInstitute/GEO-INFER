"""
Conversion utility functions for GEO-INFER-LOG.

This module provides utility functions for converting between different
units of measurement commonly used in logistics and transportation.
"""


def km_to_miles(kilometers: float) -> float:
    """
    Convert kilometers to miles.
    
    Args:
        kilometers: Distance in kilometers
        
    Returns:
        Distance in miles
    """
    return kilometers * 0.621371


def miles_to_km(miles: float) -> float:
    """
    Convert miles to kilometers.
    
    Args:
        miles: Distance in miles
        
    Returns:
        Distance in kilometers
    """
    return miles * 1.60934


def meters_to_feet(meters: float) -> float:
    """
    Convert meters to feet.
    
    Args:
        meters: Distance in meters
        
    Returns:
        Distance in feet
    """
    return meters * 3.28084


def feet_to_meters(feet: float) -> float:
    """
    Convert feet to meters.
    
    Args:
        feet: Distance in feet
        
    Returns:
        Distance in meters
    """
    return feet * 0.3048


def km_per_hour_to_mph(kph: float) -> float:
    """
    Convert kilometers per hour to miles per hour.
    
    Args:
        kph: Speed in kilometers per hour
        
    Returns:
        Speed in miles per hour
    """
    return kph * 0.621371


def mph_to_km_per_hour(mph: float) -> float:
    """
    Convert miles per hour to kilometers per hour.
    
    Args:
        mph: Speed in miles per hour
        
    Returns:
        Speed in kilometers per hour
    """
    return mph * 1.60934


def liters_to_gallons(liters: float) -> float:
    """
    Convert liters to gallons (US).
    
    Args:
        liters: Volume in liters
        
    Returns:
        Volume in gallons
    """
    return liters * 0.264172


def gallons_to_liters(gallons: float) -> float:
    """
    Convert gallons (US) to liters.
    
    Args:
        gallons: Volume in gallons
        
    Returns:
        Volume in liters
    """
    return gallons * 3.78541


def kg_to_pounds(kg: float) -> float:
    """
    Convert kilograms to pounds.
    
    Args:
        kg: Weight in kilograms
        
    Returns:
        Weight in pounds
    """
    return kg * 2.20462


def pounds_to_kg(pounds: float) -> float:
    """
    Convert pounds to kilograms.
    
    Args:
        pounds: Weight in pounds
        
    Returns:
        Weight in kilograms
    """
    return pounds * 0.453592


def cubic_meters_to_cubic_feet(cubic_meters: float) -> float:
    """
    Convert cubic meters to cubic feet.
    
    Args:
        cubic_meters: Volume in cubic meters
        
    Returns:
        Volume in cubic feet
    """
    return cubic_meters * 35.3147


def cubic_feet_to_cubic_meters(cubic_feet: float) -> float:
    """
    Convert cubic feet to cubic meters.
    
    Args:
        cubic_feet: Volume in cubic feet
        
    Returns:
        Volume in cubic meters
    """
    return cubic_feet * 0.0283168


def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius to Fahrenheit.
    
    Args:
        celsius: Temperature in Celsius
        
    Returns:
        Temperature in Fahrenheit
    """
    return (celsius * 9/5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """
    Convert Fahrenheit to Celsius.
    
    Args:
        fahrenheit: Temperature in Fahrenheit
        
    Returns:
        Temperature in Celsius
    """
    return (fahrenheit - 32) * 5/9


def minutes_to_hours(minutes: float) -> float:
    """
    Convert minutes to hours.
    
    Args:
        minutes: Time in minutes
        
    Returns:
        Time in hours
    """
    return minutes / 60


def hours_to_minutes(hours: float) -> float:
    """
    Convert hours to minutes.
    
    Args:
        hours: Time in hours
        
    Returns:
        Time in minutes
    """
    return hours * 60 