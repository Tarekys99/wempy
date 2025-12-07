"""
يحدث الخطأ عندما يكون sequence غير متزامن مع البيانات الموجودة
"""
from sqlalchemy import text
from Database.db_connect import engine

def fix_sequences():
    """إصلاح sequences للجداول"""
    
    queries = [
        # إصلاح sequence جدول types
        """
        SELECT setval(
            pg_get_serial_sequence('types', 'TypeID'),
            COALESCE((SELECT MAX("TypeID") FROM types), 0) + 1,
            false
        );
        """,
        
        # إصلاح sequence جدول sizes
        """
        SELECT setval(
            pg_get_serial_sequence('sizes', 'SizeID'),
            COALESCE((SELECT MAX("SizeID") FROM sizes), 0) + 1,
            false
        );
        """,
        
        # إصلاح sequence جدول categories
        """
        SELECT setval(
            pg_get_serial_sequence('categories', 'CategoryID'),
            COALESCE((SELECT MAX("CategoryID") FROM categories), 0) + 1,
            false
        );
        """,
        
        # إصلاح sequence جدول products
        """
        SELECT setval(
            pg_get_serial_sequence('products', 'ProductID'),
            COALESCE((SELECT MAX("ProductID") FROM products), 0) + 1,
            false
        );
        """
    ]
    
    try:
        with engine.begin() as connection:
            print("🔄 جاري إصلاح sequences...")
            
            for query in queries:
                result = connection.execute(text(query))
                print(f"✓ تم إصلاح sequence")
            
            print("\n✅ تم إصلاح جميع الـ sequences بنجاح!")
            print("يمكنك الآن إضافة بيانات جديدة بدون مشاكل.")
            
    except Exception as e:
        print(f"❌ فشل الإصلاح: {str(e)}")
        raise

if __name__ == "__main__":
    fix_sequences()
