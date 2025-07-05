#!/usr/bin/env python3
"""
Test runner for Tixel Scraper components.
Allows you to test web scraping and email sending independently.
"""

import os
import sys
import subprocess

def run_scraping_test():
    """Run the web scraping test"""
    print("🕷️  Running Web Scraping Test...")
    print("=" * 50)
    try:
        subprocess.run([sys.executable, "test_scraping.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraping test failed with exit code {e.returncode}")
    except FileNotFoundError:
        print("❌ test_scraping.py not found!")

def run_email_test():
    """Run the email sending test"""
    print("📧 Running Email Test...")
    print("=" * 50)
    try:
        subprocess.run([sys.executable, "test_email.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Email test failed with exit code {e.returncode}")
    except FileNotFoundError:
        print("❌ test_email.py not found!")

def run_full_lambda_test():
    """Run the full Lambda function test (mocked)"""
    print("🧪 Running Full Lambda Test (Mocked)...")
    print("=" * 50)
    try:
        subprocess.run([sys.executable, "test_lambda_local.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Lambda test failed with exit code {e.returncode}")
    except FileNotFoundError:
        print("❌ test_lambda_local.py not found!")

def show_menu():
    """Show the test menu"""
    print("\n🧪 Tixel Scraper Test Suite")
    print("=" * 40)
    print("Choose a test to run:")
    print("")
    print("1. 🕷️  Web Scraping Test")
    print("   - Tests ticket detection on Tixel")
    print("   - Analyzes page structure")
    print("   - No emails sent")
    print("")
    print("2. 📧 Email Test")
    print("   - Sends REAL test email")
    print("   - Validates email configuration")
    print("   - Uses actual Resend API")
    print("")
    print("3. 🧪 Full Lambda Test (Mocked)")
    print("   - Tests complete Lambda function")
    print("   - Mocks AWS services")
    print("   - No real emails sent")
    print("")
    print("4. 🔄 Run All Tests")
    print("   - Runs scraping + full Lambda test")
    print("   - Skips email test (to avoid spam)")
    print("")
    print("0. ❌ Exit")
    print("")

def main():
    """Main test runner"""
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file based on env.example:")
        print("  cp env.example .env")
        print("  # Then edit .env with your actual values")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (0-4): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                run_scraping_test()
            elif choice == '2':
                print("\n⚠️  WARNING: This will send a REAL email!")
                confirm = input("Are you sure? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    run_email_test()
                else:
                    print("❌ Email test cancelled.")
            elif choice == '3':
                run_full_lambda_test()
            elif choice == '4':
                print("🔄 Running all tests (except email)...")
                run_scraping_test()
                print("\n" + "=" * 50)
                run_full_lambda_test()
            else:
                print("❌ Invalid choice. Please enter 0-4.")
            
            if choice != '0':
                input("\n📱 Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            input("\n📱 Press Enter to continue...")

if __name__ == "__main__":
    main() 