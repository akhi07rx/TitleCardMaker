from abc import ABC, abstractmethod

from requests import get
from modules.Debug import warn

class WebInterface(ABC):
    """
    Abstract class that defines a WebInterface, which is a type of interface
    that makes GET requests and returns some JSON result. 
    """

    """How many requests to cache"""
    CACHE_LENGTH = 5
    
    @abstractmethod
    def __init__(self) -> None:
        """
        Constructs a new instance of a WebInterface. This creates creates a 
        cached request and result, but no other attributes.
        """

        # Cache of the last requests to speed up identical sequential requests
        self.__cache = []
        self.__cached_results = []


    def _get(self, url: str, params: dict) -> dict:
        """
        Wrapper for getting the JSON return of the specified GET request. If the
        provided URL and parameters are identical to the previous request, then
        a cached result is returned instead.
        
        :param      url:    URL to pass to GET.

        :param      params: Parameters to pass to GET.
        
        :returns:   Dict made from the JSON return of the specified GET request.
        """
        
        # Look through all cached results for this exact URL+params; if found,
        # skip the request and return that result
        for cache, result in zip(self.__cache, self.__cached_results):
            if cache['url'] == url and cache['params'] == str(params):
                return result

        # Make new request, add to cache
        self.__cached_results.append(get(url=url, params=params).json())
        self.__cache.append({'url': url, 'params': str(params)})

        # Delete element from cache if length has been exceeded
        if len(self.__cache) > self.CACHE_LENGTH:
            self.__cache.pop(0)
            self.__cached_results.pop(0)

        # Return latest result
        return self.__cached_results[-1]