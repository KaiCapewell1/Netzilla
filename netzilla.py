from flask import Flask, render_template, request, url_for, redirect
import get_data
import movies

def get_posters():
    get_data.Load_images()
    return get_data.all_posters

if __name__ == "__main__":
    get_posters()
