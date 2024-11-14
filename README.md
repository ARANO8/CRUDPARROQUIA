# Flask CRUD - BD-VENTAS -SQL SERVER

### Requisitos
Para ejecutar este proyecto, necesitas tener instalados los siguientes elementos:

-**PYTHON ** 3.13.0 

[Descargar Python](https://www.python.org/downloads/ "Descargar Python")

-**SQL Server 2019 Express**

 [Descargar SQL Server 2019 Express](Download Microsoft® SQL Server® 2019 Express from Official Microsoft Download Center "Descargar SQL Server 2019 Express")
 
### Instalación
Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local:
1. Clona el repositorio

    `$ git clone https://github.com/jafernandez22/CRUD-SQLSERVER.git`

2.  Sigue los pasos del pdf guia

`https://drive.google.com/file/d/1pBmTl3W4lEBOtBcPZHEIk5WgIwlsQudF/view?usp=sharing `


Nota: En SqlServer-BDVENTAS hacer correr lo siguiente:

    ---crear en sql procedimiento
    CREATE PROCEDURE dbo.ObtenerDetalleFactura2
        @num_fac VARCHAR(12)
    AS
    BEGIN
        SELECT 
            DF.NUM_FAC,
            P.DES_PRO AS Producto,
            DF.CAN_VEN AS Cantidad,
            DF.PRE_VEN AS PrecioUnitario,
            (DF.CAN_VEN * DF.PRE_VEN) AS Subtotal
        FROM DETALLE_FACTURA DF
        JOIN PRODUCTO P ON DF.COD_PRO = P.COD_PRO
        WHERE DF.NUM_FAC = @num_fac;
    END;
    GO
    
    ---crear en sql vista
    CREATE VIEW VISTAPRODUCTOSPROVEEDOR AS
    SELECT 
        PR.COD_PRV,
        PR.RSO_PRV AS Proveedor,
        P.COD_PRO,
        P.DES_PRO AS Producto,
        A.PRE_ABA AS PrecioAbastecimiento
    FROM PROVEEDOR PR
    JOIN ABASTECIMIENTO A ON PR.COD_PRV = A.COD_PRV
    JOIN PRODUCTO P ON A.COD_PRO = P.COD_PRO;
    GO
   
